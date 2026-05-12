"""
Import the finished tools and show what each one returns.

The implementations live in utils/tools.py. In the next file, we'll hand these
same three functions to an LLM as tools.

More info: https://docs.python.org/3/library/pathlib.html
"""

from utils.tools import grep, list_files, read_file

# --------------------------------------------------------------
# Tool 1: list_files. Discover what's in the notes folder.
# --------------------------------------------------------------

print("Files in notes/:")
for f in list_files():
    print(f"  {f}")


# --------------------------------------------------------------
# Tool 2: grep. Find lines matching a pattern across all files.
# --------------------------------------------------------------

print("\nGrep for 'connection pool':")
for hit in grep("connection pool"):
    print(f"  {hit}")


# --------------------------------------------------------------
# Tool 3: read_file. Pull the full body of one file.
# --------------------------------------------------------------

print("\nFirst 200 chars of 04-architecture-decisions.md:")
print(read_file("04-architecture-decisions.md")[:200])
