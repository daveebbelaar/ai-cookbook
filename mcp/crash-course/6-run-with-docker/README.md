# MCP Server with Docker

This project demonstrates how to run an MCP (Model Context Protocol) server using Docker. The server provides a simple calculator tool that can be accessed by a client.

## Prerequisites

- Docker installed on your system
- Git (to clone the repository)

## Project Structure

- `server.py`: The MCP server implementation with a simple calculator tool
- `client.py`: A client that connects to the server and calls the calculator tool
- `Dockerfile`: Instructions for building the Docker image
- `requirements.txt`: Python dependencies for the project

## Running with Docker

### Step 1: Build the Docker image

```bash
docker build -t mcp-server .
```

### Step 2: Run the Docker container

```bash
docker run --rm -p 127.0.0.1:8050:8050 mcp-server
```

This starts the MCP server inside Docker and publishes port 8050 only on your machine. Run these Docker commands from `mcp/crash-course/6-run-with-docker`.

## Running the Client

Once the server is running, you can run the client in a separate terminal:

```bash
# Activate the course environment and install ../requirements.txt first
python client.py
```

The client will connect to the server, list available tools, and call the calculator tool to add 2 and 3.

## Troubleshooting

If you encounter connection issues:

1. **Check if the server is running**: Make sure the Docker container is running with `docker ps`.

2. **Verify port mapping**: Ensure the port is correctly mapped with `docker ps` or by checking the output of the `docker run` command.

3. **Check server logs**: View the server logs with `docker logs <container_id>` to see if there are any errors.

4. **Host binding**: The server is configured to bind to `0.0.0.0` instead of `127.0.0.1` to make it accessible from outside the container. If you're still having issues, you might need to check your firewall settings.

5. **Host/Origin errors**: The server explicitly allows `localhost:8050` and `127.0.0.1:8050`, even though it binds to all interfaces inside Docker. Do not disable DNS rebinding protection to fix a rejected request. This unauthenticated example is intended for local use.

## Notes

- The server is configured to use SSE (Server-Sent Events) transport and listens on port 8050.
- The client connects to the server at `http://localhost:8050/sse`.
- Make sure the server is running before starting the client. 