# MCP Crash Course for Python Developers

This is the companion code for my [MCP Crash Course](https://www.youtube.com/watch?v=5xqFjh56AwM). Work through the same seven sections as the video: build a calculator server, connect Python clients, integrate OpenAI, and run the server in Docker.

## Following the original video

**Use the requirements in this folder, even when the video shows an older version.** The examples now pin `mcp[cli]==1.30.0`, the maintained v1 SDK, instead of the vulnerable `1.10.1`. FastMCP, ClientSession, tool names, filenames, and lesson order stay the same.

The [SDK's current major version is v2](https://github.com/modelcontextprotocol/python-sdk), which changes these APIs. I am keeping this tutorial on the supported v1 line so you can follow the recording. Do not replace the pin with an unversioned `pip install mcp`. See the [v1 documentation](https://py.sdk.modelcontextprotocol.io/v1/) and [v1.30.0 release notes](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v1.30.0).

| Video chapter | Follow along today |
| --- | --- |
| 12:29, environment setup | Install the updated requirements below, including the missing `nest-asyncio` dependency. |
| 16:56, server setup | Same FastMCP calculator. Local HTTP binds to `127.0.0.1`; stdio logs go to stderr. |
| 25:48, Python clients | Same stdio and SSE clients. Streamable HTTP is also available in section 3. |
| 33:39, OpenAI integration | Same Chat Completions tool loop and knowledge base. Clients now resolve paths independently of your working directory and close connections on errors. |
| 49:29, function calling | Same direct function-calling comparison. |
| 51:07, Docker | Same SSE example; publish with `-p 127.0.0.1:8050:8050` and keep Host/Origin validation enabled. |
| 54:19, lifecycle | Clients initialize and close MCP sessions as before. |

**SSE remains here for video compatibility.** For new HTTP integrations, use [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http). These unauthenticated examples are for local learning; publishing a port does not add authentication.

## Table of contents

1. [Introduction and context](./1-introduction-and-context/README.md)
2. [Understanding MCP](./2-understanding-mcp/README.md)
3. [Simple server setup with Python SDK](./3-simple-server-setup/README.md)
4. [OpenAI integration](./4-openai-integration/README.md)
5. [MCP vs function calling](./5-mcp-vs-function-calling/README.md)
6. [Running with Docker](./6-run-with-docker/README.md)
7. [Lifecycle management](./7-lifecycle-management/README.md)

## Set up your development environment

From the repository root, using Python 3.11 or newer:

```bash
cd mcp/crash-course
uv venv --python 3.11
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

Or use Python's built-in environment tools:

```bash
cd mcp/crash-course
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Keep this environment active in each terminal. For the interactive Python workflow shown in the video, select this environment as your kernel and set the working directory to the numbered lesson folder before running cells. Sections 4 and 5 need `OPENAI_API_KEY` in `mcp/crash-course/.env` (copy `.env.example` without overwriting an existing file). The calculator examples need no API key.

```bash
python 3-simple-server-setup/client-stdio.py
# Expected: the add tool is listed, then 2 + 3 = 5
```

The CLI still works with this pinned SDK:

```bash
mcp dev 3-simple-server-setup/server.py
mcp install 3-simple-server-setup/server.py
```

`mcp dev` opens the MCP Inspector and requires Node.js/npm. `mcp install` updates Claude Desktop's configuration. The Python clients can be run without either application.
