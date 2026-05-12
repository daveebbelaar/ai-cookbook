"""
Canonical search tools for the agentic-search tutorial:
list_files, grep, and read_file over a folder of markdown notes.

Imported by 2-import-tools.py, 3-basic-agent.py, 4-streaming-steps.py,
and 5-structured-output.py. File 6-production.py defines its own
ripgrep-backed versions to show the production swap.
"""

import re
from pathlib import Path

NOTES_DIR = (Path(__file__).parents[1] / "notes").resolve()


def list_files(pattern: str = "*.md") -> list[str]:
    """List markdown files in the notes directory matching a glob pattern."""
    return sorted(str(p.relative_to(NOTES_DIR)) for p in NOTES_DIR.glob(pattern))


def grep(pattern: str, max_results: int = 30) -> list[str]:
    """
    Search all markdown files in the notes directory for lines matching `pattern`
    (case-insensitive regex). Returns lines as 'file:lineno: text'.
    """
    rx = re.compile(pattern, re.IGNORECASE)
    hits: list[str] = []
    for f in sorted(NOTES_DIR.rglob("*.md")):
        for i, line in enumerate(f.read_text().splitlines(), start=1):
            if rx.search(line):
                rel = f.relative_to(NOTES_DIR)
                hits.append(f"{rel}:{i}: {line.strip()}")
                if len(hits) >= max_results:
                    return hits
    return hits


def read_file(path: str) -> str:
    """Read a markdown file by relative path. Refuses paths outside the notes directory."""
    target = (NOTES_DIR / path).resolve()
    if not target.is_relative_to(NOTES_DIR):
        raise ValueError(f"Path {path} is outside the notes directory")
    return target.read_text()
