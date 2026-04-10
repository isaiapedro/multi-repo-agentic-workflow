import logging

from github import GithubException
from github.Repository import Repository

from portfolio_manager.config import readme_context_max_chars

logger = logging.getLogger(__name__)

_SKIP_SEGMENTS = frozenset(
    {
        "node_modules",
        "vendor",
        "__pycache__",
        ".git",
        "venv",
        ".venv",
        "dist",
        "build",
        ".next",
        "target",
        ".gradle",
        ".idea",
        ".vscode",
        "coverage",
        "htmlcov",
    }
)

_BINARY_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp4",
    ".mp3",
    ".wasm",
)

_PRIORITY_NAMES = [
    "readme.md",
    "readme.rst",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "pipfile",
    "cargo.toml",
    "go.mod",
    "go.work",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "makefile",
    "justfile",
    "tsconfig.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "gemfile",
    "composer.json",
]

_PER_FILE_CAP = 12000


def _should_skip_path(path: str) -> bool:
    lower = path.lower().replace("\\", "/")
    for segment in lower.split("/"):
        if segment in _SKIP_SEGMENTS:
            return True
    base = lower.rsplit("/", 1)[-1]
    return any(base.endswith(s) for s in _BINARY_SUFFIXES)


def _path_priority(path: str) -> tuple[int, str]:
    lower = path.lower().replace("\\", "/")
    base = lower.rsplit("/", 1)[-1]
    try:
        idx = _PRIORITY_NAMES.index(base)
        return (idx, path)
    except ValueError:
        return (len(_PRIORITY_NAMES), path)


def _format_repo_header(repo: Repository) -> str:
    try:
        topic_list = repo.get_topics()
    except Exception:
        topic_list = []
    topics = ", ".join(topic_list) if topic_list else ""
    lic = repo.license
    lic_name = lic.name if lic else ""
    lines = [
        f"Repository: {repo.full_name}",
        f"Default branch: {repo.default_branch}",
        f"Description (current): {repo.description or ''}",
        f"Primary language: {repo.language or 'unknown'}",
        f"Topics: {topics}",
        f"Homepage: {repo.homepage or ''}",
        f"License (GitHub metadata): {lic_name}",
        f"Archived: {repo.archived}",
        f"Fork: {repo.fork}",
        f"Private: {repo.private}",
    ]
    return "\n".join(lines)


def _read_file_text(repo: Repository, path: str, ref: str) -> str | None:
    try:
        content = repo.get_contents(path, ref=ref)
    except GithubException as exc:
        if getattr(exc, "status", None) == 404:
            return None
        logger.debug("Skip path %s: %s", path, exc)
        return None
    if isinstance(content, list):
        return None
    if content.size and content.size > _PER_FILE_CAP * 2:
        return None
    try:
        data = content.decoded_content
        text = data.decode("utf-8", errors="replace")
    except Exception:
        return None
    if len(text) > _PER_FILE_CAP:
        text = text[:_PER_FILE_CAP] + "\n... [truncated]"
    return text


def gather_repository_context(repo: Repository) -> str:
    ref = repo.default_branch
    parts: list[str] = [_format_repo_header(repo)]
    max_total = readme_context_max_chars()
    used = len(parts[0])

    try:
        branch = repo.get_branch(ref)
        tree = repo.get_git_tree(branch.commit.sha, recursive=True)
    except GithubException as exc:
        logger.warning("Could not load git tree for %s: %s", repo.full_name, exc)
        return parts[0]

    paths: list[str] = []
    for item in tree.tree:
        if item.type != "blob" or not item.path:
            continue
        if _should_skip_path(item.path):
            continue
        paths.append(item.path)

    paths.sort(key=_path_priority)

    for path in paths:
        if used >= max_total:
            break
        base = path.rsplit("/", 1)[-1].lower()
        if base.endswith(tuple(_BINARY_SUFFIXES)):
            continue
        text = _read_file_text(repo, path, ref)
        if not text:
            continue
        block = f"### File: {path}\n\n```\n{text}\n```"
        chunk_len = len(block) + 2
        if used + chunk_len > max_total:
            remain = max_total - used - 100
            if remain < 500:
                break
            text = text[: max(0, remain - 200)] + "\n... [truncated]"
            block = f"### File: {path}\n\n```\n{text}\n```"
            chunk_len = len(block) + 2
        parts.append(block)
        used += chunk_len

    return "\n\n".join(parts)
