# ai.market MCP Server — legacy stdio client

## Current compatibility

For the current hosted customer connector, use `https://connect.ai.market` and the ai.market connector setup instructions. This repository is the older stdio client; the installation, examples and tool descriptions below record that implementation and are not a verified current purchase or delivery workflow.

Source comparison on 2026-10-11 (client `d3bab634`, backend `d5307fcc`) confirms:

- The client sends `X-API-Key`, but does not supply the OAuth Bearer header required by current purchase and wallet-write routes. A successful connection check with zero balance or empty orders does not establish access to the customer's wallet or order history.
- `get_order_data` calls `/agent/orders/{id}/data`, which is absent from the current Agent router. Current purchased delivery uses seller-controlled infrastructure; this client is not evidence of a working download route.
- `AIMARKET_SANDBOX` adds a request header. The old mock-data, fake-balance and no-charge statements below are not end-to-end safety guarantees; do not use a paid action to diagnose compatibility.

The existing operator reference is [Legacy MCP client runbook](https://github.com/aidotmarket/runbooks/blob/main/aimarket-mcp-server.md) (authorized repository access required). This notice does not retire the package, verify registry availability, or claim a live customer journey.

## Historical implementation and setup


MCP (Model Context Protocol) server for the [ai.market](https://ai.market) data marketplace. Enables LLM clients like Claude Desktop, Cursor, and Cline to search, evaluate, and purchase datasets.

## Features

- **Search datasets** by natural language query
- **Get detailed information** about datasets including schema, pricing, and compliance
- **Preview sample data** before purchasing
- **Check wallet balance** and manage funds
- **Purchase datasets** directly from your LLM client
- **Access purchased data** via signed download URLs
- **Sandbox mode** for testing without real charges

## Installation

### Option 1: Install from PyPI

```bash
pip install aimarket-mcp-server
```

### Option 2: Install from source

```bash
git clone https://github.com/aidotmarket/aimarket-mcp-server.git
cd aimarket-mcp-server
pip install -e .
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AIMARKET_API_KEY` | Your ai.market API key | None |
| `AIMARKET_SANDBOX` | Enable sandbox mode | `false` |
| `AIMARKET_BASE_URL` | API base URL | Production URL |
| `AIMARKET_TIMEOUT` | Request timeout (seconds) | `30` |

### Getting an API Key

1. Sign up at [ai.market](https://ai.market)
2. Go to Settings → API Keys
3. Create a new API key
4. Copy the key and set it as `AIMARKET_API_KEY`

### Sandbox Mode

For testing without real charges, enable sandbox mode:

```bash
export AIMARKET_SANDBOX=true
```

In sandbox mode:
- Uses mock datasets (5 sample datasets)
- $1,000 fake wallet balance
- No real purchases or charges

## Claude Desktop Configuration

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aimarket": {
      "command": "python",
      "args": ["-m", "aimarket_mcp.server"],
      "env": {
        "AIMARKET_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or for sandbox mode:

```json
{
  "mcpServers": {
    "aimarket": {
      "command": "python",
      "args": ["-m", "aimarket_mcp.server"],
      "env": {
        "AIMARKET_SANDBOX": "true"
      }
    }
  }
}
```

Then restart Claude Desktop.

## Available Tools

### Discovery

| Tool | Description |
|------|-------------|
| `search_datasets` | Search for datasets by natural language query |
| `get_dataset` | Get detailed information about a dataset |
| `evaluate_dataset` | Get schema, statistics, and compliance info |
| `preview_dataset` | Get sample rows from a dataset |

### Transactions

| Tool | Description |
|------|-------------|
| `check_wallet` | Get current wallet balance |
| `purchase_dataset` | Purchase a dataset (requires confirmation) |
| `list_orders` | List your orders |
| `get_order_data` | Get download URL for purchased data |

### Utility

| Tool | Description |
|------|-------------|
| `verify_connection` | Test API connection and credentials |

## Usage Examples

Once configured, you can use natural language with Claude:

> "Search for e-commerce transaction datasets"

> "Show me the details for dataset 00000000-0000-0000-0000-000000000001"

> "Check my wallet balance"

> "Purchase the financial market dataset" (requires confirmation)

> "List my recent orders"

## Security

- API keys are never logged or exposed in tool outputs
- Purchase operations require explicit confirmation
- Sandbox mode prevents accidental real purchases
- All API communications use HTTPS

## Development

```bash
# Clone the repository
git clone https://github.com/aidotmarket/aimarket-mcp-server.git
cd aimarket-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: [docs.ai.market](https://docs.ai.market)
- Issues: [GitHub Issues](https://github.com/aidotmarket/aimarket-mcp-server/issues)
- Email: support@ai.market
