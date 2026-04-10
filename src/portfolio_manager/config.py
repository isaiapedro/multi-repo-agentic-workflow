import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    max_retries: int = 3
    fast_model: str = "gpt-4o-mini"
    smart_model: str = "gpt-4o"
    run_mode: str = "manual_cli"


def postgres_connection_kwargs():
    return {
        "dbname": os.environ.get("POSTGRES_DB", "postgres"),
        "user": os.environ.get("POSTGRES_USER", "postgres"),
        "password": os.environ.get("POSTGRES_PASSWORD", ""),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
    }


def log_file_path():
    return os.environ.get("AGENT_LOG_FILE", "agent_runs.log")


def github_repo_affiliation():
    return os.environ.get("GITHUB_REPO_AFFILIATION", "owner")


def github_repo_exclude_forks() -> bool:
    v = os.environ.get("GITHUB_REPO_EXCLUDE_FORKS", "true").lower()
    return v in ("1", "true", "yes")
