"""
MCP Server for Render.com API
Provides tools to interact with Render services (deploy, logs, status, etc.)
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Render API Configuration
RENDER_API_BASE_URL = "https://api.render.com/v1"
RENDER_API_KEY = os.getenv("RENDER_API_KEY")


class RenderAPIClient:
    """Client for interacting with Render API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request to Render API"""
        url = f"{RENDER_API_BASE_URL}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
    
    async def get_services(self) -> list[dict[str, Any]]:
        """Get all services"""
        return await self._request("GET", "/services")
    
    async def get_service(self, service_id: str) -> dict[str, Any]:
        """Get a specific service by ID"""
        return await self._request("GET", f"/services/{service_id}")
    
    async def get_service_logs(
        self,
        service_id: str,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get logs for a service"""
        return await self._request(
            "GET",
            f"/services/{service_id}/logs?limit={limit}"
        )
    
    async def get_deployments(self, service_id: str) -> list[dict[str, Any]]:
        """Get deployments for a service"""
        return await self._request("GET", f"/services/{service_id}/deploys")
    
    async def trigger_deploy(self, service_id: str) -> dict[str, Any]:
        """Trigger a new deploy for a service"""
        return await self._request(
            "POST",
            f"/services/{service_id}/deploys",
            json={}
        )
    
    async def get_owner(self) -> dict[str, Any]:
        """Get current owner/account info"""
        return await self._request("GET", "/owners/me")


# Global client instance
render_client = RenderAPIClient(RENDER_API_KEY) if RENDER_API_KEY else None


# MCP Server Tools
async def list_services() -> str:
    """List all Render services"""
    if not render_client:
        return "Error: RENDER_API_KEY not configured. Please set it in .env file."
    
    try:
        services = await render_client.get_services()
        if not services:
            return "No services found."
        
        result = "## Render Services\n\n"
        for service in services:
            result += f"- **{service.get('name', 'Unknown')}** ({service.get('type', 'Unknown')})\n"
            result += f"  - ID: {service.get('id', 'N/A')}\n"
            result += f"  - Status: {service.get('serviceDetail', {}).get('status', 'N/A')}\n"
            result += f"  - Region: {service.get('region', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        return f"Error fetching services: {str(e)}"


async def get_service_status(service_id: str) -> str:
    """Get status of a specific service"""
    if not render_client:
        return "Error: RENDER_API_KEY not configured. Please set it in .env file."
    
    try:
        service = await render_client.get_service(service_id)
        
        result = f"## Service: {service.get('name', 'Unknown')}\n\n"
        result += f"- **ID:** {service.get('id', 'N/A')}\n"
        result += f"- **Type:** {service.get('type', 'N/A')}\n"
        result += f"- **Status:** {service.get('serviceDetail', {}).get('status', 'N/A')}\n"
        result += f"- **Region:** {service.get('region', 'N/A')}\n"
        result += f"- **Created At:** {service.get('createdAt', 'N/A')}\n"
        result += f"- **Updated At:** {service.get('updatedAt', 'N/A')}\n"
        
        # Environment variables (non-sensitive info)
        env_vars = service.get('envVars', [])
        if env_vars:
            result += f"\n**Environment Variables:**\n"
            for env in env_vars[:5]:  # Show first 5
                result += f"- {env.get('key', 'N/A')}: {env.get('value', '****')}\n"
        
        return result
    except Exception as e:
        return f"Error fetching service status: {str(e)}"


async def get_service_logs(service_id: str, limit: int = 100) -> str:
    """Get logs for a specific service"""
    if not render_client:
        return "Error: RENDER_API_KEY not configured. Please set it in .env file."
    
    try:
        logs = await render_client.get_service_logs(service_id, limit)
        
        if not logs:
            return "No logs found for this service."
        
        result = f"## Service Logs (Last {limit} entries)\n\n"
        for log in logs:
            timestamp = log.get('timestamp', 'N/A')
            message = log.get('message', '')
            level = log.get('level', 'INFO')
            result += f"[{timestamp}] [{level}] {message}\n"
        
        return result
    except Exception as e:
        return f"Error fetching logs: {str(e)}"


async def get_deployments(service_id: str) -> str:
    """Get deployment history for a service"""
    if not render_client:
        return "Error: RENDER_API_KEY not configured. Please set it in .env file."
    
    try:
        deployments = await render_client.get_deployments(service_id)
        
        if not deployments:
            return "No deployments found for this service."
        
        result = "## Deployment History\n\n"
        for deploy in deployments[:10]:  # Show last 10
            result += f"- **Commit:** {deploy.get('commitId', 'N/A')[:7]}\n"
            result += f"  - Status: {deploy.get('status', 'N/A')}\n"
            result += f"  - Created: {deploy.get('createdAt', 'N/A')}\n"
            result += f"  - Finished: {deploy.get('finishedAt', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        return f"Error fetching deployments: {str(e)}"


async def trigger_deploy(service_id: str) -> str:
    """Trigger a new deploy for a service"""
    if not render_client:
        return "Error: RENDER_API_KEY not configured. Please set it in .env file."
    
    try:
        result = await render_client.trigger_deploy(service_id)
        return f"Deploy triggered successfully!\n\nDeploy ID: {result.get('id', 'N/A')}\nStatus: {result.get('status', 'N/A')}"
    except Exception as e:
        return f"Error triggering deploy: {str(e)}"


async def get_account_info() -> str:
    """Get current account information"""
    if not render_client:
        return "Error: RENDER_API_KEY not configured. Please set it in .env file."
    
    try:
        owner = await render_client.get_owner()
        return f"## Account Information\n\n" \
               f"- **ID:** {owner.get('id', 'N/A')}\n" \
               f"- **Email:** {owner.get('email', 'N/A')}\n" \
               f"- **Name:** {owner.get('name', 'N/A')}"
    except Exception as e:
        return f"Error fetching account info: {str(e)}"


# Main entry point for MCP server
def main():
    """Main entry point for the MCP server"""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    
    server = Server("render-api-server")
    
    @server.list_tools()
    async def list_tools():
        return [
            {
                "name": "list_services",
                "description": "List all Render services in your account",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_service_status",
                "description": "Get detailed status of a specific Render service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The Render service ID"
                        }
                    },
                    "required": ["service_id"]
                }
            },
            {
                "name": "get_service_logs",
                "description": "Get logs for a specific Render service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The Render service ID"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of log entries to fetch (default: 100)",
                            "default": 100
                        }
                    },
                    "required": ["service_id"]
                }
            },
            {
                "name": "get_deployments",
                "description": "Get deployment history for a specific Render service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The Render service ID"
                        }
                    },
                    "required": ["service_id"]
                }
            },
            {
                "name": "trigger_deploy",
                "description": "Trigger a new deploy for a specific Render service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "The Render service ID to deploy"
                        }
                    },
                    "required": ["service_id"]
                }
            },
            {
                "name": "get_account_info",
                "description": "Get current account information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> str:
        if name == "list_services":
            return await list_services()
        elif name == "get_service_status":
            return await get_service_status(arguments.get("service_id"))
        elif name == "get_service_logs":
            return await get_service_logs(
                arguments.get("service_id"),
                arguments.get("limit", 100)
            )
        elif name == "get_deployments":
            return await get_deployments(arguments.get("service_id"))
        elif name == "trigger_deploy":
            return await trigger_deploy(arguments.get("service_id"))
        elif name == "get_account_info":
            return await get_account_info()
        else:
            return f"Unknown tool: {name}"
    
    # Run the server
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
