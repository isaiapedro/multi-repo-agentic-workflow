import logging
import uuid

from github import Github, GithubException

from portfolio_manager.config import github_update_repo_description, load_agent_config
from portfolio_manager.db import OrchestratorDB
from portfolio_manager.github_ops import create_agent_pr, update_repository_description
from portfolio_manager.readme_llm import (
    generate_github_description_line,
    generate_readme_with_escalation,
)
from portfolio_manager.repo_context import gather_repository_context

logger = logging.getLogger(__name__)


def run_orchestrator(g: Github, repo_list: list[str]):
    config = load_agent_config()
    db = OrchestratorDB()

    logger.info("Starting Manual Run for %s repos...", len(repo_list))

    for repo_full_name in repo_list:
        logger.info("Processing repository: %s", repo_full_name)
        db.insert_new_run(repo_full_name, "running")

        retry_count = 0
        success = False

        while retry_count < config.max_retries and not success:
            try:
                try:
                    repo = g.get_repo(repo_full_name)
                except GithubException as exc:
                    logger.error("Cannot access repository %s: %s", repo_full_name, exc)
                    raise

                logger.info("[%s] Ingesting repository context from GitHub API...", repo_full_name)
                context = gather_repository_context(repo)

                logger.info("[%s] Generating README from ingested context...", repo_full_name)
                readme_body, used_smart = generate_readme_with_escalation(
                    context, repo_full_name, config
                )
                if used_smart:
                    logger.warning(
                        "[%s] Escalated README generation to %s",
                        repo_full_name,
                        config.smart_model,
                    )

                if github_update_repo_description():
                    try:
                        desc = generate_github_description_line(
                            context,
                            readme_body,
                            repo_full_name,
                            config.fast_model,
                        )
                        update_repository_description(repo, desc)
                    except Exception as exc:
                        logger.warning("[%s] Skipping description update: %s", repo_full_name, exc)

                branch_name = f"agent/portfolio-readme-{uuid.uuid4().hex[:12]}"
                logger.info(
                    "[%s] Creating pull request (branch %s)...",
                    repo_full_name,
                    branch_name,
                )
                pr_created = create_agent_pr(
                    repo_full_name=repo_full_name,
                    branch_name=branch_name,
                    file_path="README.md",
                    content=readme_body,
                    commit_message="docs: regenerate README from ingested repository context",
                )

                if pr_created:
                    success = True
                    db.update_run_status(repo_full_name, "completed")
                else:
                    raise RuntimeError("PR creation returned False")

            except Exception as e:
                retry_count += 1
                logger.error(
                    "[%s] Run failed (Attempt %s/%s): %s",
                    repo_full_name,
                    retry_count,
                    config.max_retries,
                    e,
                )
                if retry_count >= config.max_retries:
                    logger.critical(
                        "[%s] Hard failing after %s retries. Manual intervention required.",
                        repo_full_name,
                        config.max_retries,
                    )
                    db.update_run_status(repo_full_name, "failed")
