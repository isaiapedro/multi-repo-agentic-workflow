import logging
import sys

from dotenv import load_dotenv

from portfolio_manager.config import github_repo_affiliation, github_repo_exclude_forks
from portfolio_manager.github_ops import github_client, list_user_repository_full_names
from portfolio_manager.logging_setup import configure_logging
from portfolio_manager.orchestrator import run_orchestrator


def main():
    load_dotenv()
    configure_logging()
    log = logging.getLogger(__name__)
    g = github_client()
    if not g:
        log.error("GITHUB_TOKEN is not set")
        sys.exit(1)
    repos = list_user_repository_full_names(
        g,
        affiliation=github_repo_affiliation(),
        exclude_forks=github_repo_exclude_forks(),
    )
    if not repos:
        log.warning("No repositories matched your filters; nothing to do.")
        return
    log.info("Discovered %s repositories", len(repos))
    run_orchestrator(repos)


if __name__ == "__main__":
    main()
