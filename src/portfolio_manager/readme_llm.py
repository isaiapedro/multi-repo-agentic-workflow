import logging
import re

from openai import OpenAI

from portfolio_manager.config import AgentConfig, llm_temperature, openai_api_key, openai_base_url

logger = logging.getLogger(__name__)


def _openai_compatible_client() -> OpenAI:
    base = openai_base_url()
    key = openai_api_key()
    if base:
        return OpenAI(base_url=base, api_key=key or "ollama")
    if not key:
        raise RuntimeError(
            "Set OPENAI_API_KEY for api.openai.com, or set OPENAI_BASE_URL for a local "
            "OpenAI-compatible server (for example Ollama at http://localhost:11434/v1)."
        )
    return OpenAI(api_key=key)


_SYSTEM_README = (
    "You are a senior technical writer. Output exactly one GitHub-flavored Markdown document. "
    "Use only facts supported by the repository context below. If the context does not mention "
    "something, write that it is not documented here instead of guessing. Do not invent "
    "features, versions, URLs, or commands. "
    "Required structure: "
    "(1) Single line at top: short project name as # heading matching the repository purpose. "
    "(2) ## Overview: 2–5 sentences on what the project does and who it is for. "
    "(3) ## Tech stack: languages, frameworks, and key dependencies named in the context. "
    "(4) ## Getting started: prerequisites, install, and how to run or build using only "
    "commands or steps inferable from files in the context. "
    "(5) ## Project layout: brief explanation of important top-level folders or modules if "
    "discernible from paths and snippets. "
    "(6) ## Testing: how to run tests or 'Not documented in repository' if absent. "
    "(7) ## Configuration: environment variables or config files referenced in the context, or "
    "state none found. "
    "(8) ## License: name or link if present in context; otherwise 'See repository files'. "
    "Use bullet lists where they improve clarity. Include fenced code blocks only for real "
    "commands or config taken from the context. "
    "Do not wrap the full document in an outer markdown code fence."
)

_SYSTEM_DESC = (
    "Given repository metadata and a README draft, output a single plain line suitable for the "
    "GitHub repository description field (max 350 characters). "
    "No quotes, no markdown, one line only."
)

_MIN_README_CHARS = 600


def _strip_wrapping_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n```$", "", t)
    return t.strip()


def _call_chat(client: OpenAI, model: str, system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=llm_temperature(),
    )
    choice = resp.choices[0]
    content = choice.message.content
    if not content:
        raise RuntimeError("empty completion")
    return content


def generate_readme_markdown(
    context: str,
    repo_full_name: str,
    config: AgentConfig,
    force_smart: bool = False,
) -> str:
    client = _openai_compatible_client()
    user_msg = f"Repository full name: {repo_full_name}\n\nRepository context follows.\n\n{context}"
    model = config.smart_model if force_smart else config.fast_model
    raw = _call_chat(client, model, _SYSTEM_README, user_msg)
    return _strip_wrapping_fence(raw)


def generate_readme_with_escalation(
    context: str,
    repo_full_name: str,
    config: AgentConfig,
) -> tuple[str, bool]:
    used_smart = False
    try:
        text = generate_readme_markdown(context, repo_full_name, config, force_smart=False)
    except Exception as exc:
        logger.warning("Fast model README generation failed: %s", exc)
        text = generate_readme_markdown(context, repo_full_name, config, force_smart=True)
        used_smart = True
    if len(text.strip()) < _MIN_README_CHARS:
        if not used_smart:
            logger.info("README short or empty; escalating to smart model")
            text = generate_readme_markdown(context, repo_full_name, config, force_smart=True)
            used_smart = True
        else:
            logger.warning("README remains short after smart model output")
    return text, used_smart


def generate_github_description_line(
    context: str,
    readme_markdown: str,
    repo_full_name: str,
    model: str,
) -> str:
    client = _openai_compatible_client()
    user_msg = (
        f"Repository: {repo_full_name}\n\n"
        f"Context excerpt:\n{context[:8000]}\n\n"
        f"README draft:\n{readme_markdown[:8000]}"
    )
    line = _call_chat(client, model, _SYSTEM_DESC, user_msg).strip().splitlines()[0]
    if len(line) > 350:
        line = line[:347] + "..."
    return line
