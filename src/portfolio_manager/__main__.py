from portfolio_manager.logging_setup import configure_logging
from portfolio_manager.orchestrator import run_orchestrator


def main():
    configure_logging()
    my_repos = ["data-pipeline-v1", "flutter-app-demo"]
    run_orchestrator(my_repos)


if __name__ == "__main__":
    main()
