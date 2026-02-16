"""
Snowflake MCP Server (stdio transport)
--------------------------------------

This file defines a single MCP tool:

    run_query(sql: str) -> { columns, row_count, rows }

The tool:
  - Connects to Snowflake using credentials in environment variables / .env
  - Only allows *read‑only* SQL (SELECT / WITH / SHOW / DESCRIBE / EXPLAIN)
  - Returns query results as a list of row dictionaries

MCP-wise, you can think of this as:
  1. Start server
  2. Tell client "I support the tool run_query"
  3. Wait for requests
  4. Run the tool
  5. Return results
  6. Repeat
"""

import os
from typing import Any, Dict, List

import snowflake.connector
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

# Load variables from a local .env file, if present.
# Example .env contents:
#   SNOWFLAKE_ACCOUNT=abc-xyz
#   SNOWFLAKE_USER=MY_USER
#   SNOWFLAKE_PASSWORD=super-secret
#   SNOWFLAKE_ROLE=ANALYST
#   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
#   SNOWFLAKE_DATABASE=MY_DB
#   SNOWFLAKE_SCHEMA=PUBLIC
load_dotenv()


def _get_required_env(name: str) -> str:
    """Return an environment variable or raise a clear error if missing."""
    value = os.getenv(name)
    if not value:
        # Raising here makes configuration problems obvious at startup.
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_snowflake_connection() -> snowflake.connector.SnowflakeConnection:
    """Create a *new* Snowflake connection using environment variables.

    We intentionally create a new connection per call (instead of a global,
    long‑lived connection) to keep things simple and robust for a first MCP
    server.
    """
    # Required connection pieces – if any are missing, we fail fast.
    kwargs: Dict[str, Any] = {
        "account": _get_required_env("SNOWFLAKE_ACCOUNT"),
        "user": _get_required_env("SNOWFLAKE_USER"),
        "password": _get_required_env("SNOWFLAKE_PASSWORD"),
    }

    # Optional configuration – we only add these if they are set.
    # (Snowflake is fine with them being omitted.)
    optional_keys = ["role", "warehouse", "database", "schema"]
    for key in optional_keys:
        env_name = f"SNOWFLAKE_{key.upper()}"
        value = os.getenv(env_name)
        if value:
            kwargs[key] = value

    return snowflake.connector.connect(**kwargs)


# ---------------------------------------------------------------------------
# Read‑only SQL guard
# ---------------------------------------------------------------------------

# Anything starting with these prefixes is treated as "read‑only enough" for
# this simple server. You can expand or tighten this list later.
READ_ONLY_PREFIXES = ("SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN")


def is_read_only_sql(sql: str) -> bool:
    """Return True if the SQL *appears* read‑only based on its first keyword.

    This is intentionally simple and conservative. It won't catch every edge
    case, but it's a good starting safety net.
    """
    # Strip leading whitespace and grab the first word (if any).
    first_token = sql.lstrip().split(maxsplit=1)[0].upper() if sql.strip() else ""
    if not first_token:
        return False
    return any(first_token.startswith(prefix) for prefix in READ_ONLY_PREFIXES)


# ---------------------------------------------------------------------------
# MCP server + tool definition
# ---------------------------------------------------------------------------

# Create the MCP server that will expose our Snowflake tool.
mcp = FastMCP("SnowflakeMCP")


# The @mcp.tool() decorator tells the MCP server:
#   "treat this Python function as a tool that clients can discover and call."
# It registers the function's name, docstring, and type hints so that when a
# client calls list_tools() it will see `run_query`, and when it sends a
# call_tool request the library handles all the JSON ↔ Python conversion.
@mcp.tool()
def run_query(sql: str) -> Dict[str, Any]:
    """Run a read‑only SQL query against Snowflake.

    Args:
        sql:
            The SQL statement to execute. For safety, this must be a
            read‑only statement whose first keyword is one of:
            SELECT, WITH, SHOW, DESCRIBE, EXPLAIN.

    Returns:
        A dictionary with:
          - columns: list of column names (strings)
          - row_count: how many rows were returned
          - rows: list of dictionaries, one per row

        Example:
            {
              "columns": ["ID", "NAME"],
              "row_count": 2,
              "rows": [
                {"ID": 1, "NAME": "Alice"},
                {"ID": 2, "NAME": "Bob"},
              ],
            }
    """
    # Basic safety check to keep this tool read‑only.
    if not is_read_only_sql(sql):
        raise ValueError(
            "Only read‑only queries are allowed. "
            "Start your statement with SELECT, WITH, SHOW, DESCRIBE, or EXPLAIN."
        )

    # Open a *fresh* connection for each call.
    # The context managers ensure the connection and cursor are closed cleanly.
    with get_snowflake_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

            # If the query returns rows (e.g. SELECT), build a list of dicts.
            if cur.description:
                columns: List[str] = [col[0] for col in cur.description]
                raw_rows = cur.fetchall()
                rows: List[Dict[str, Any]] = [
                    dict(zip(columns, row)) for row in raw_rows
                ]
            else:
                # Some read‑only statements (e.g. certain SHOW commands)
                # might not return a traditional result set.
                columns = []
                rows = []

    return {
        "columns": columns,
        "row_count": len(rows),
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run the MCP server using stdio transport.
    #
    # From a terminal, you can test it with:
    #   uv run server.py
    #
    # Or via MCP Inspector:
    #   mcp dev server.py
    mcp.run(transport="stdio")


