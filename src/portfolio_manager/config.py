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


def openai_api_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "")


def openai_base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL", "").strip()


def llm_is_configured() -> bool:
    if openai_base_url():
        return True
    return bool(openai_api_key())


def load_agent_config() -> AgentConfig:
    has_local = bool(openai_base_url())
    default_fast = "llama3.2" if has_local else "gpt-4o-mini"
    default_smart = "llama3.2" if has_local else "gpt-4o"
    return AgentConfig(
        max_retries=int(os.environ.get("AGENT_MAX_RETRIES", "3")),
        fast_model=os.environ.get("LLM_FAST_MODEL", default_fast),
        smart_model=os.environ.get("LLM_SMART_MODEL", default_smart),
        run_mode=os.environ.get("AGENT_RUN_MODE", "manual_cli"),
    )


def llm_temperature() -> float:
    return float(os.environ.get("LLM_TEMPERATURE", "0.2"))


def github_update_repo_description() -> bool:
    v = os.environ.get("GITHUB_UPDATE_REPO_DESCRIPTION", "false").lower()
    return v in ("1", "true", "yes")


def readme_context_max_chars() -> int:
    return int(os.environ.get("README_CONTEXT_MAX_CHARS", "60000"))
