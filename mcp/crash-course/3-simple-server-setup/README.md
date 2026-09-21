# Simple Server Setup with Python SDK

**The calculator and clients match the original video.** Install the [course requirements](../README.md#set-up-your-development-environment) first. Run the commands below from `mcp/crash-course` with that environment active.

## Build and run the server

`server.py` uses `FastMCP` and exposes `add(a: int, b: int) -> int` through `@mcp.tool()`. The transport defaults to stdio. You can still change the `transport` variable as shown in the video, or pass it on the command line.

### stdio: the video default

```bash
python 3-simple-server-setup/client-stdio.py
```

The client launches the server as a **separate subprocess**, initializes the session, lists tools, and calls `add`. You do not start the server separately. The subprocess uses the client's Python environment. stdout carries protocol messages, so server diagnostics go to stderr.

### SSE: the original HTTP example

Terminal 1:

```bash
python 3-simple-server-setup/server.py sse
```

Terminal 2:

```bash
python 3-simple-server-setup/client-sse.py
```

The client connects to `http://localhost:8050/sse`. This older transport remains available so you can follow the recording.

### Streamable HTTP: for new HTTP integrations

Terminal 1:

```bash
python 3-simple-server-setup/server.py streamable-http
```

Terminal 2:

```bash
python 3-simple-server-setup/client-streamable-http.py
```

The client connects to `http://localhost:8050/mcp`. Stop the previous server before switching transports, since both use port 8050.

All three clients should list `add` and print `2 + 3 = 5`.

## Choose a transport

| Transport | Client setup | Use |
| --- | --- | --- |
| stdio | `stdio_client`, then `ClientSession` | Launch a local server subprocess |
| SSE | `sse_client`, then `ClientSession` | Follow the video or connect to an older server |
| Streamable HTTP | `streamablehttp_client`, then `ClientSession` | New HTTP integrations, one `/mcp` endpoint |

Streamable HTTP replaces the older HTTP+SSE transport in the [MCP transport specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports). This example uses stateless HTTP; do not assume the server retains conversation state between requests.

## Inspector and Claude Desktop

```bash
mcp dev 3-simple-server-setup/server.py
mcp install 3-simple-server-setup/server.py
```

The Inspector requires Node.js/npm. The install command requires Claude Desktop and changes its configuration. Both use the same `mcp` instance and tool definitions.

## Local security defaults

HTTP binds to `127.0.0.1`. The patched SDK enables DNS rebinding protection for loopback hosts. Keep these settings for the local tutorial. An external deployment needs explicit trusted hosts/origins and appropriate authentication; changing the bind address alone is not sufficient. See the [v1 SDK documentation](https://py.sdk.modelcontextprotocol.io/v1/).
