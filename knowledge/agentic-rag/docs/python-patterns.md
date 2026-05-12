# Python patterns used in this tutorial

This tutorial uses a few Python standard library features that are easy to read once you know the pattern, but not obvious if you do not use them every day.

The big idea: **`pathlib` gives us safe, readable file paths, and `re` gives us reusable text search patterns.**

## Quick reference

| Pattern | Where you see it | What it does | Simple description |
| --- | --- | --- | --- |
| `Path(__file__)` | `Path(__file__).parent` | Converts the current file name into a `Path` object. | Start from the file this code lives in. |
| `.parent` | `Path(__file__).parent` | Gets the folder that contains a path. | Move from the file to its directory. |
| `/` with paths | `Path(__file__).parent / "notes"` | Joins path parts in a cross-platform way. | Build `folder/notes` without string concatenation. |
| `.resolve()` | `(NOTES_DIR / path).resolve()` | Turns a path into an absolute normalized path. | Collapse `..`, symlinks, and relative pieces. |
| `.glob(pattern)` | `NOTES_DIR.glob("*.md")` | Finds files matching a pattern in a directory. | List matching files, usually one folder deep unless the pattern includes `**`. |
| `.rglob(pattern)` | `NOTES_DIR.rglob("*.md")` | Recursively finds files matching a pattern. | Search this folder and every subfolder. |
| `.relative_to(base)` | `p.relative_to(NOTES_DIR)` | Returns the path relative to a base directory, or raises an error if it cannot. | Turn `/repo/notes/a.md` into `a.md`. |
| `.is_relative_to(base)` | `path.is_relative_to(NOTES_DIR)` | Checks whether a path lives under a base path. | Ask: "Is this still inside the notes folder?" |
| `.is_file()` | `path.is_file()` | Checks whether the path points to a regular file. | Keep files, skip folders. |
| `.exists()` | `safe.exists()` | Checks whether the path exists on disk. | Give a friendly error before reading. |
| `.read_text()` | `safe.read_text(encoding="utf-8")` | Reads a text file into one string. | Open and read the file in one call. |
| `.splitlines()` | `read_text().splitlines()` | Splits text into a list of lines without newline characters. | Make file content easy to loop over line by line. |
| `enumerate(..., start=1)` | `enumerate(lines, start=1)` | Loops over items while also counting them. | Get human-friendly line numbers. |
| `re.compile(pattern, re.IGNORECASE)` | `rx = re.compile(pattern, re.IGNORECASE)` | Turns a regex string into a reusable regex object. | Prepare the search once, then reuse it. |
| `rx.search(line)` | `if rx.search(line):` | Looks for the regex anywhere inside a string. | Does this line contain a match? |

## The path pattern

In this tutorial, all file access starts from the tutorial file itself:

```python
NOTES_DIR = (Path(__file__).parent / "notes").resolve()
```

Read it left to right:

1. `Path(__file__)` starts with the current Python file.
2. `.parent` gets the folder containing that file.
3. `/ "notes"` joins the `notes` folder onto that path.
4. `.resolve()` turns the result into a clean absolute path.

That gives every tool a stable root folder, no matter where you run Python from.

## `glob` vs `rglob`

Use `glob` when you want files matching a pattern from one directory:

```python
NOTES_DIR.glob("*.md")
```

Use `rglob` when you want to search through all nested folders too:

```python
NOTES_DIR.rglob("*.md")
```

For this tutorial, `glob` is enough for listing the top-level note files. `rglob` is useful in `grep` because search tools usually expect to search a whole tree, not only one folder.

## The safety pattern

The production version validates paths before reading:

```python
target = (NOTES_DIR / path).resolve()
if not target.is_relative_to(NOTES_DIR):
    return None
```

This matters because the agent supplies `path`. If the agent asks for `../secrets.txt`, `.resolve()` reveals the real destination, and `.is_relative_to(NOTES_DIR)` rejects it because it escaped the allowed folder.

## The regex pattern

In `utils/tools.py`, `grep` compiles the pattern once:

```python
rx = re.compile(pattern, re.IGNORECASE)
```

Then it checks each line:

```python
if rx.search(line):
    ...
```

That reads as: "prepare a case-insensitive search pattern, then keep each line where the pattern appears anywhere in the text."

## Resources

- [Python `pathlib` documentation](https://docs.python.org/3/library/pathlib.html)
- [Python `re` documentation](https://docs.python.org/3/library/re.html)
