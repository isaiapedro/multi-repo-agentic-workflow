import logging

from portfolio_manager.config import AgentConfig
from portfolio_manager.db import OrchestratorDB
from portfolio_manager.github_ops import create_agent_pr

logger = logging.getLogger(__name__)


def run_orchestrator(repo_list: list):
    config = AgentConfig()
    db = OrchestratorDB()

    logger.info("Starting Manual Run for %s repos...", len(repo_list))

    for repo in repo_list:
        logger.info("Processing repository: %s", repo)
        db.insert_new_run(repo, "running")

        retry_count = 0
        success = False

        while retry_count < config.max_retries and not success:
            try:
                logger.info("[%s] Running ingestion with %s...", repo, config.fast_model)

                needs_complex_fix = False
                if needs_complex_fix:
                    logger.warning(
                        "[%s] Complex issue detected. Escalating to %s...",
                        repo,
                        config.smart_model,
                    )

                new_readme_content = "# Updated Repository\nManaged by Agent."

                logger.info("[%s] Proposing changes via PR...", repo)
                pr_created = create_agent_pr(
                    repo_full_name=repo,
                    branch_name="agent/readme-update",
                    file_path="README.md",
                    content=new_readme_content,
                    commit_message="Refactor README using Vector DB context",
                )

                if pr_created:
                    success = True
                    db.update_run_status(repo, "completed")
                else:
                    raise RuntimeError("PR creation returned False")

            except Exception as e:
                retry_count += 1
                logger.error(
                    "[%s] Run failed (Attempt %s/%s): %s",
                    repo,
                    retry_count,
                    config.max_retries,
                    e,
                )
                if retry_count >= config.max_retries:
                    logger.critical(
                        "[%s] Hard failing after %s retries. Manual intervention required.",
                        repo,
                        config.max_retries,
                    )
                    db.update_run_status(repo, "failed")
