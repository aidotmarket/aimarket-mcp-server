"""
ai.market MCP Server
====================

MCP server for the ai.market data marketplace.
Enables LLM clients to search, evaluate, and purchase datasets.
"""

from .server import main, app
from .client import client, AIMarketClient
from .config import config, Config

__version__ = "0.1.0"
__all__ = ["main", "app", "client", "AIMarketClient", "config", "Config"]
