"""
Production-ready tools.

Same three-tool interface as `utils/tools.py`, but with production constraints:
bounded outputs, path validation, tool-call logging, and agent-readable errors.

More info: https://github.com/BurntSushi/ripgrep
"""

import logging
import platform
import shutil
import subprocess
import time
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent, UsageLimits
import nest_asyncio

nest_asyncio.apply()

NOTES_DIR = (Path(__file__).parent / "notes").resolve()
GREP_TIMEOUT_SECONDS = 30
READ_MAX_LINES = 200
AGENT_REQUEST_LIMIT = 20

logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Step 1: Environment helpers
# --------------------------------------------------------------


def _ripgrep_install_hint() -> str:
    """Return the most relevant ripgrep install command for this OS."""
    system = platform.system()
    if system == "Darwin":
        return "Install with `brew install ripgrep`."
    if system == "Windows":
        return "Install with `winget install BurntSushi.ripgrep.MSVC`, `choco install ripgrep`, or `scoop install ripgrep`."
    return (
        "Install with your package manager, for example `sudo apt-get install ripgrep`."
    )


# --------------------------------------------------------------
# Step 2: Path validation helper
# --------------------------------------------------------------


def _safe_path(path: str) -> Path | None:
    """Resolve a user-supplied path against NOTES_DIR."""
    target = (NOTES_DIR / path).resolve()
    if not target.is_relative_to(NOTES_DIR):
        return None
    return target


# --------------------------------------------------------------
# Step 3: grep with ripgrep
# --------------------------------------------------------------


def grep(pattern: str, max_results: int = 30, context: int = 0) -> str:
    """Search markdown notes with ripgrep and return matching `file:line:text` lines.

    Set `context` to include N surrounding lines around each match (rg -C). Recently
    edited files come first via `--sortr=modified`. `--no-config` ignores any user
    `~/.ripgreprc` so behavior is identical across machines.
    """
    logger.info(
        "grep(pattern=%r, max_results=%d, context=%d)", pattern, max_results, context
    )

    if max_results < 1:
        return "Error: max_results must be 1 or greater."
    if context < 0:
        return "Error: context must be 0 or greater."
    if not shutil.which("rg"):
        return f"Error: ripgrep ('rg') is not installed. {_ripgrep_install_hint()}"

    cmd = [
        "rg",
        "--line-number",
        "--no-heading",
        "--ignore-case",
        "--no-config",
        "--sortr=modified",
        "--max-count",
        str(max_results),
        "--glob",
        "*.md",
        *(["--context", str(context)] if context > 0 else []),
        "--",
        pattern,
        ".",
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=NOTES_DIR,
            capture_output=True,
            text=True,
            check=False,
            timeout=GREP_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        logger.warning("grep timed out for pattern=%r", pattern)
        return f"Error: grep timed out after {GREP_TIMEOUT_SECONDS}s. Try a more specific pattern."

    if result.returncode == 2:
        return f"Error: invalid pattern {pattern!r}: {result.stderr.strip()}"

    if not result.stdout.strip():
        return f"No matches found for pattern: {pattern}"

    lines = result.stdout.splitlines()
    if len(lines) > max_results:
        lines = lines[:max_results] + [
            f"... truncated to {max_results} matches. Try a more specific pattern."
        ]
    return "\n".join(lines)


# --------------------------------------------------------------
# Step 4: list files safely
# --------------------------------------------------------------


def list_files(pattern: str = "*.md") -> str:
    """List files in the notes directory using a glob pattern."""
    logger.info("list_files(pattern=%r)", pattern)

    if not NOTES_DIR.exists():
        return f"Error: notes directory not found at {NOTES_DIR}"

    try:
        paths = NOTES_DIR.glob(pattern)
    except (NotImplementedError, ValueError) as e:
        return f"Error: invalid glob pattern {pattern!r}: {e}"

    matches = sorted(
        str(path.relative_to(NOTES_DIR))
        for path in (p.resolve() for p in paths)
        if path.is_file() and path.is_relative_to(NOTES_DIR)
    )
    if not matches:
        return f"No files matched pattern: {pattern}"
    return "\n".join(matches)


# --------------------------------------------------------------
# Step 5: read bounded file ranges
# --------------------------------------------------------------


def read_file(path: str, offset: int = 1, limit: int = READ_MAX_LINES) -> str:
    """Read a bounded line range from a file relative to the notes root."""
    logger.info("read_file(path=%r, offset=%d, limit=%d)", path, offset, limit)

    safe = _safe_path(path)
    if safe is None:
        return f"Error: path {path!r} is outside the notes directory."
    if not safe.exists():
        return f"Error: file not found: {path}"
    if not safe.is_file():
        return f"Error: {path} is not a file."
    if offset < 1:
        return "Error: offset must be 1 or greater."
    if limit < 1:
        return "Error: limit must be 1 or greater."
    if limit > READ_MAX_LINES:
        return f"Error: limit must be {READ_MAX_LINES} lines or fewer."

    try:
        lines = safe.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return f"Error: {path} is not UTF-8 text."

    end = min(offset + limit - 1, len(lines))
    excerpt = lines[offset - 1 : end]
    if not excerpt:
        return f"No lines found. {path} has {len(lines)} lines."
    return "\n".join(f"{i}: {line}" for i, line in enumerate(excerpt, start=offset))


# --------------------------------------------------------------
# Step 6: Structured answer models
# --------------------------------------------------------------


class Citation(BaseModel):
    """One source backing a claim in the answer."""

    file: str = Field(
        description="Relative path to the markdown file, e.g. '03-incident-2024-q3.md'"
    )
    quote: str = Field(description="Exact line(s) from the file that support the claim")


class SearchAnswer(BaseModel):
    """Structured answer with citations that downstream code can trust."""

    answer: str = Field(description="The answer in plain English")
    citations: list[Citation] = Field(
        description="Files and quotes that support the answer"
    )


# --------------------------------------------------------------
# Step 7: Production agent
# --------------------------------------------------------------


agent = Agent(
    # "openai:gpt-5.5",
    "openai:gpt-4.1-nano",  # faster
    tools=[list_files, grep, read_file],
    output_type=SearchAnswer,
    instructions=(
        "Answer from notes with citations. Use grep context or read_file ranges. "
        "Adapt to Error/No matches."
    ),
)


# --------------------------------------------------------------
# Step 8: Run it with a turn cap
# --------------------------------------------------------------


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    start = time.perf_counter()
    result = agent.run_sync(
        "Why does our nightly deploy job run at 03:47 UTC specifically?",
        usage_limits=UsageLimits(request_limit=AGENT_REQUEST_LIMIT),
    )
    elapsed = time.perf_counter() - start

    print("\nAgent:", result.output.answer)
    print("\nCitations:")
    for citation in result.output.citations:
        print(f"  - {citation.file}")
        for line in citation.quote.splitlines():
            print(f"      {line}")

    usage = result.usage()
    print(
        f"\nUsage: {usage.requests} requests, {usage.tool_calls} tool calls, "
        f"{usage.input_tokens} input + {usage.output_tokens} output tokens, "
        f"{elapsed:.1f}s"
    )
