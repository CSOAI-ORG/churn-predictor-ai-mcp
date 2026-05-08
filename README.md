<div align="center">

# Churn Predictor Ai MCP

**MCP server for churn predictor ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-churn-predictor-ai-mcp)](https://pypi.org/project/meok-churn-predictor-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Churn Predictor Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `predict_churn` | Predict churn risk for a customer |
| `batch_predict_churn` | Predict churn for multiple customers |
| `get_customer_risk` | Get current risk score for a customer |
| `track_customer` | Add customer to churn tracking |
| `update_customer_signals` | Update customer behavioral signals |
| `get_at_risk_customers` | Get all customers above risk threshold |
| `create_retention_action` | Create a retention action for at-risk customer |
| `get_retention_actions` | Get retention actions for a customer |
| `update_retention_action` | Update status of retention action |
| `get_churn_analytics` | Get overall churn analytics |
| `get_cohort_retention` | Get cohort retention analysis |
| `simulate_intervention` | Simulate impact of retention action |
| `get_risk_trends` | Get risk score trends over time |

## Installation

```bash
pip install meok-churn-predictor-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "churn-predictor-ai": {
      "command": "python",
      "args": ["-m", "meok_churn_predictor_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 13 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
