# Short UV Guide

Quick steps to set up a Python project with [uv](https://github.com/astral-sh/uv).

---

## 1. Install uv (one-time, machine-level)

```bash
brew install uv
```

## 2. Install the Python version you want to pin

```bash
uv python install 3.13
```

## 3. Go to your project directory

```bash
mkdir your_project
cd your_project
```

## 4. Initialize uv project metadata

Creates `pyproject.toml`.

```bash
uv init
```

## 5. Pin Python 3.13 for this project

Creates `.python-version`.

```bash
uv python pin 3.13
```

## 6. Import existing dependencies from requirements.txt

Updates `pyproject.toml` and creates `uv.lock` (dependency pin).

```bash
uv add -r requirements.txt
```

## 7. Create a virtual environment

Uses the pinned Python version.

```bash
uv venv
```

## 8. Install exact, locked dependencies into the venv. Recommended after every uv add "something"

```bash
uv sync
```

## 9. Activate the virtual environment

```bash
source .venv/bin/activate
```

## 10. Verify the project is using the pinned Python

```bash
uv run python --version
```
