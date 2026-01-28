# MCP Server for Render.com - Setup Guide

This guide explains how to set up and configure the MCP server for Render.com API.

## Prerequisites

- Python 3.10+
- Render API Key (get it from https://dashboard.render.com/account)
- pip or poetry for dependency management

## Installation

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

Or if you want to install individually:

```bash
pip install mcp>=1.0.0 httpx>=0.25.0 python-dotenv
```

2. **Configure API Key**

Create or update your `.env` file with your Render API key:

```bash
RENDER_API_KEY=your_render_api_key_here
```

You can get your API key from:
- Go to https://dashboard.render.com/account
- Scroll down to "API Keys"
- Create a new API key or use an existing one

## Configuration

### MCP Settings (`mcp_settings.json`)

Add the following configuration to your `mcp_settings.json` file:

```json
{
  "mcpServers": {
    "render": {
      "command": "python",
      "args": ["${workspaceFolder}/mcp_render_server.py"],
      "env": {
        "RENDER_API_KEY": "${env:RENDER_API_KEY}"
      }
    }
  }
}
```

**Note:** The `RENDER_API_KEY` will be read from your system's environment variables.

### Alternative: Direct Environment Variable

If you prefer, you can set the environment variable directly:

**Windows (Command Prompt):**
```cmd
set RENDER_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:RENDER_API_KEY="your_api_key_here"
```

**Linux/macOS:**
```bash
export RENDER_API_KEY="your_api_key_here"
```

## Available Tools

Once configured, the following tools will be available:

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_services` | List all Render services in your account | None |
| `get_service_status` | Get detailed status of a specific service | `service_id` (required) |
| `get_service_logs` | Get logs for a specific service | `service_id` (required), `limit` (optional, default: 100) |
| `get_deployments` | Get deployment history for a service | `service_id` (required) |
| `trigger_deploy` | Trigger a new deploy for a service | `service_id` (required) |
| `get_account_info` | Get current account information | None |

## Usage Examples

### List All Services

```
Tool: list_services
Result: Shows all services with their status and region
```

### Check Service Status

```
Tool: get_service_status
Parameters: {"service_id": "srv-xxxxx"}
Result: Shows detailed service information
```

### View Service Logs

```
Tool: get_service_logs
Parameters: {"service_id": "srv-xxxxx", "limit": 50}
Result: Shows last 50 log entries
```

### Trigger a Deploy

```
Tool: trigger_deploy
Parameters: {"service_id": "srv-xxxxx"}
Result: Confirms deploy was triggered
```

## Troubleshooting

### "RENDER_API_KEY not configured" Error

1. Make sure you've set the `RENDER_API_KEY` environment variable
2. Restart your IDE/MCP client after setting the environment variable
3. Check that your `.env` file is in the correct location

### API Errors

1. Verify your Render API key is valid
2. Check that you have the necessary permissions on Render
3. Ensure the service ID is correct

### Dependency Issues

If you encounter issues with the `mcp` package, try:

```bash
pip install --upgrade mcp
```

## Security Notes

- Never commit your `.env` file with real API keys to version control
- Use `.env.example` as a template for required environment variables
- Consider using a dedicated API key with minimal permissions for MCP

## API Reference

For more information about the Render API, see:
- [Render API Documentation](https://render.com/docs/api)
- [Render API Reference](https://api.render.com/docs)
