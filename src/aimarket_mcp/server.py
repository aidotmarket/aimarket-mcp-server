"""
ai.market MCP Server
====================

MCP (Model Context Protocol) server that exposes the ai.market Agent API
as tools for LLM clients like Claude Desktop, Cursor, and other MCP-enabled agents.

TOOLS PROVIDED:
    - search_datasets: Search for datasets by query
    - get_dataset: Get dataset details
    - evaluate_dataset: Get schema, statistics, compliance info
    - preview_dataset: Get sample rows
    - check_wallet: Get wallet balance
    - purchase_dataset: Purchase a dataset (requires confirmation)
    - list_orders: List your orders
    - get_order_data: Get download URL for purchased data
    - verify_connection: Test API connection

USAGE:
    # Set API key
    export AIMARKET_API_KEY="your_api_key"
    
    # Or enable sandbox mode (no real charges)
    export AIMARKET_SANDBOX="true"
    
    # Run server
    python -m aimarket_mcp.server

Phase: 4.2 (MCP Integration)
Created: 2026-01-25
"""

import asyncio
import json
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

from .client import client, APIError


# Create MCP server
app = Server("aimarket")


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    Tool(
        name="search_datasets",
        description="""Search the ai.market data marketplace for datasets.
        
Use this when you need to find datasets for a specific use case.
Returns a list of matching datasets with relevance scores.

Tips for better results:
- Be specific about data type (e.g., 'financial transactions', 'customer reviews')
- Include industry or domain (e.g., 'healthcare', 'e-commerce')""",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query (e.g., 'e-commerce transactions')"
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (optional)"
                },
                "max_price_cents": {
                    "type": "integer",
                    "description": "Maximum price in cents (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_dataset",
        description="""Get detailed information about a specific dataset.
        
Returns full details including description, schema summary, pricing, 
seller info, and compliance certifications.""",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "UUID of the dataset"
                }
            },
            "required": ["dataset_id"]
        }
    ),
    Tool(
        name="evaluate_dataset",
        description="""Get deep evaluation data for a dataset before purchase.
        
Returns complete schema, column statistics, quality score, 
completeness metrics, PII risk level, and compliance details.""",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "UUID of the dataset"
                }
            },
            "required": ["dataset_id"]
        }
    ),
    Tool(
        name="preview_dataset",
        description="""Get a preview of sample rows from a dataset.
        
Returns up to 10 anonymized sample rows to verify data format and content.""",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "UUID of the dataset"
                },
                "rows": {
                    "type": "integer",
                    "description": "Number of rows to preview (max 10)",
                    "default": 5
                }
            },
            "required": ["dataset_id"]
        }
    ),
    Tool(
        name="check_wallet",
        description="""Check your ai.market wallet balance.
        
Returns current balance, currency, and top-up URL.
In sandbox mode, you have a $1,000 test balance.""",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="purchase_dataset",
        description="""Purchase access to a dataset using your wallet balance.
        
⚠️ IMPORTANT: This will deduct real funds from your wallet!
Make sure you have sufficient balance before purchasing.

The purchase is immediate - funds are deducted and the order is created.
Use list_orders and get_order_data to access your purchased data.""",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {
                    "type": "string",
                    "description": "UUID of the dataset to purchase"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Set to true to confirm the purchase"
                },
                "note": {
                    "type": "string",
                    "description": "Optional note for the order"
                }
            },
            "required": ["dataset_id", "confirm"]
        }
    ),
    Tool(
        name="list_orders",
        description="""List your dataset orders.
        
Returns order history including status, price, and purchase date.""",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by status (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max orders to return (default: 20)",
                    "default": 20
                }
            }
        }
    ),
    Tool(
        name="get_order_data",
        description="""Get download URL for purchased dataset.
        
Returns a signed download URL that expires after 1 hour.""",
        inputSchema={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "UUID of the order"
                },
                "format": {
                    "type": "string",
                    "description": "Download format (csv, parquet, json)",
                    "default": "csv"
                }
            },
            "required": ["order_id"]
        }
    ),
    Tool(
        name="verify_connection",
        description="""Verify connection to ai.market API.
        
Tests that your API key is valid and the server is reachable.
Also reports sandbox mode status.""",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
]


# =============================================================================
# TOOL HANDLERS
# =============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        result = await _execute_tool(name, arguments)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    except APIError as e:
        error_response = {
            "error": True,
            "status_code": e.status_code,
            "message": e.message,
            "details": e.details
        }
        return [TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": True,
                "message": str(e)
            }, indent=2)
        )]


async def _execute_tool(name: str, arguments: dict) -> dict:
    """Execute a tool and return the result."""
    
    if name == "search_datasets":
        return await client.search_datasets(
            query=arguments["query"],
            category=arguments.get("category"),
            max_price_cents=arguments.get("max_price_cents"),
            limit=arguments.get("limit", 10)
        )
    
    elif name == "get_dataset":
        return await client.get_dataset(arguments["dataset_id"])
    
    elif name == "evaluate_dataset":
        return await client.evaluate_dataset(arguments["dataset_id"])
    
    elif name == "preview_dataset":
        return await client.preview_dataset(
            arguments["dataset_id"],
            rows=arguments.get("rows", 5)
        )
    
    elif name == "check_wallet":
        return await client.get_wallet_balance()
    
    elif name == "purchase_dataset":
        # Safety check - require explicit confirmation
        if not arguments.get("confirm"):
            return {
                "error": True,
                "message": "Purchase not confirmed. Set confirm=true to proceed.",
                "warning": "This will deduct funds from your wallet!"
            }
        
        return await client.purchase_dataset(
            dataset_id=arguments["dataset_id"],
            note=arguments.get("note")
        )
    
    elif name == "list_orders":
        return await client.list_orders(
            status=arguments.get("status"),
            limit=arguments.get("limit", 20)
        )
    
    elif name == "get_order_data":
        return await client.get_order_data(
            order_id=arguments["order_id"],
            format=arguments.get("format", "csv")
        )
    
    elif name == "verify_connection":
        return await client.verify_connection()
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# =============================================================================
# MAIN
# =============================================================================

async def run():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
