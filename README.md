# Churn Predictor AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Customer churn prediction, retention analytics, and intervention simulation

## Installation

```bash
pip install churn-predictor-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install churn-predictor-ai-mcp
```

## Tools

### `predict_churn`
Predict churn risk for a customer based on behavioral signals.

**Parameters:**
- `customer_id` (str): Customer identifier
- `last_login_days` (int): Days since last login
- `support_tickets_last_30d` (int): Support tickets in last 30 days
- `nps_score` (int): NPS score (1-10)
- `usage_decline_percent` (int): Usage decline percentage
- `payment_failures` (int): Number of payment failures
- `tenure_months` (int): Customer tenure in months

### `batch_predict_churn`
Predict churn for multiple customers at once.

**Parameters:**
- `customers` (list): List of customer data dicts

### `get_customer_risk`
Get current risk score for a tracked customer.

**Parameters:**
- `customer_id` (str): Customer identifier

### `track_customer`
Add customer to churn tracking system.

**Parameters:**
- `customer_id` (str): Customer identifier
- `initial_data` (dict): Initial behavioral data

### `update_customer_signals`
Update customer behavioral signals and recalculate risk.

**Parameters:**
- `customer_id` (str): Customer identifier
- `signals` (dict): Updated signal data

### `get_at_risk_customers`
Get all customers above a risk score threshold.

**Parameters:**
- `threshold` (int): Risk score threshold (default 60)
- `limit` (int): Max results (default 50)

### `create_retention_action`
Create a retention action for an at-risk customer.

**Parameters:**
- `customer_id` (str): Customer identifier
- `action_type` (str): Action type (outreach, discount, upgrade, etc.)
- `description` (str): Action description

### `get_retention_actions`
Get retention actions filtered by customer or status.

**Parameters:**
- `customer_id` (str): Filter by customer
- `status` (str): Filter by status

### `update_retention_action`
Update status of a retention action.

**Parameters:**
- `action_id` (str): Action identifier
- `status` (str): New status

### `get_churn_analytics`
Get overall churn analytics for a period (7d, 30d, 90d).

**Parameters:**
- `period` (str): Time period (default '30d')

### `get_cohort_retention`
Get cohort retention analysis.

**Parameters:**
- `cohort_month` (str): Cohort month

### `simulate_intervention`
Simulate the impact of a retention action on customer risk score.

**Parameters:**
- `customer_id` (str): Customer identifier
- `action_type` (str): Action type (outreach, discount, upgrade, survey, bonus)

### `get_risk_trends`
Get risk score trends over time for a customer.

**Parameters:**
- `customer_id` (str): Customer identifier
- `days` (int): Number of days to look back (default 30)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
