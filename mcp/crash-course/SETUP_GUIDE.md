# MCP Crash Course Setup Guide

## Prerequisites

Before starting this course, ensure you have:

- Python 3.11 or higher
- Git installed and configured
- GitHub account with SSH keys set up
- Docker Desktop (for Module 6)
- A code editor (VS Code recommended)
- OpenAI API key (for Module 4)

## Initial Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub first, then:
git clone git@github.com:YOUR_USERNAME/ai-cookbook.git
cd ai-cookbook/mcp/crash-course
```

### 2. Create Virtual Environment

You have two options for Python environment management:

#### Option A: Traditional venv (Recommended for beginners)

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Option B: Using uv (Faster, used in original course)

```bash
# Install uv if you don't have it
pip install uv

# Create virtual environment with uv
uv venv

# Activate it (same as traditional venv)
source venv/bin/activate  # macOS/Linux
# or
# venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# If using traditional pip:
pip install -r requirements.txt

# If using uv (faster):
uv pip install -r requirements.txt
```

**Note**: The original course examples use `uv` for faster package installation, but both methods work perfectly. We recommend starting with traditional `venv` if you're new to Python development.

### 4. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Verify Installation

```bash
# Check MCP CLI is installed
mcp --version

# Test Python environment
python -c "import mcp; print('MCP installed successfully')"
```

## GitHub Workflow Setup

### 1. Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Install GitHub CLI

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Windows
winget install --id GitHub.cli
```

### 3. Authenticate GitHub CLI

```bash
gh auth login
```

## IDE Setup (VS Code)

### Recommended Extensions

Install these VS Code extensions for the best experience:

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff
code --install-extension ms-azuretools.vscode-docker
code --install-extension github.vscode-pull-request-github
```

### Workspace Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

## Testing Your Setup

### 1. Test MCP Inspector

```bash
cd 3-simple-server-setup
mcp dev server.py
```

This should open the MCP Inspector in your browser.

### 2. Test Simple Client

```bash
cd 3-simple-server-setup
python client-stdio.py
```

Expected output:
```
Available tools:
  - add: Add two numbers together
2 + 3 = 5
```

### 3. Test GitHub Integration

```bash
# Create a test issue
gh issue create --title "Setup Test" --body "Testing GitHub CLI integration"

# List issues
gh issue list
```

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'mcp'**
   - Ensure your virtual environment is activated
   - Reinstall with: `pip install -r requirements.txt`

2. **OpenAI API Error**
   - Check your API key is correctly set in `.env`
   - Ensure you have credits in your OpenAI account

3. **Permission Denied (GitHub)**
   - Check SSH keys: `ssh -T git@github.com`
   - Re-authenticate: `gh auth login`

4. **Port Already in Use**
   - Change the port in server configuration
   - Kill existing process: `lsof -ti:8050 | xargs kill -9`

### Getting Help

- Course Discord: [Join here](#)
- GitHub Discussions: Use the repo's Discussions tab
- Office Hours: Thursdays 2-3 PM EST

## Next Steps

Once your setup is complete:

1. Create your first issue for Module 1
2. Create your feature branch
3. Start with the [EDUCATIONAL_MODULE.md](./EDUCATIONAL_MODULE.md) guide

Happy learning!