#!/usr/bin/env python3
"""MEOK AI Labs — churn-predictor-ai-mcp MCP Server. Comprehensive customer churn prediction and retention analytics."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
from collections import defaultdict
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

_store = {"customers": {}, "predictions": [], "retention_actions": [], "cohorts": {}}

mcp = FastMCP("churn-predictor-ai", instructions="Comprehensive customer churn prediction and retention analytics.")


def create_id():
    return str(uuid.uuid4())[:8]


def calculate_risk_score(customer_data: dict) -> dict:
    score = 0
    factors = []

    last_login_days = customer_data.get("last_login_days", 0)
    if last_login_days > 30:
        score += 40
        factors.append(f"No login for {last_login_days} days")
    elif last_login_days > 14:
        score += 20
        factors.append(f"Inactive for {last_login_days} days")

    support_tickets = customer_data.get("support_tickets_last_30d", 0)
    if support_tickets > 5:
        score += 30
        factors.append(f"{support_tickets} support tickets in 30 days")
    elif support_tickets > 2:
        score += 15

    nps = customer_data.get("nps_score", 5)
    if nps <= 3:
        score += 35
        factors.append(f"Low NPS score: {nps}")
    elif nps <= 5:
        score += 15

    usage_decline = customer_data.get("usage_decline_percent", 0)
    if usage_decline > 50:
        score += 30
        factors.append(f"{usage_decline}% usage decline")
    elif usage_decline > 25:
        score += 15

    payment_failures = customer_data.get("payment_failures", 0)
    if payment_failures >= 2:
        score += 25
        factors.append(f"{payment_failures} payment failures")

    tenure_months = customer_data.get("tenure_months", 0)
    if tenure_months < 3 and score > 20:
        score += 10
        factors.append("New customer with risk indicators")

    at_risk = score >= 60
    high_risk = score >= 80

    return {
        "risk_score": min(100, score),
        "risk_level": "critical"
        if high_risk
        else "high"
        if at_risk
        else "medium"
        if score >= 40
        else "low",
        "factors": factors,
        "recommendation": "immediate_intervention"
        if high_risk
        else "monitor"
        if at_risk
        else "keep"
        if score < 20
        else "engage",
    }


@mcp.tool()
def predict_churn(customer_id: str = "unknown", last_login_days: int = 0, support_tickets_last_30d: int = 0, nps_score: int = 5, usage_decline_percent: int = 0, payment_failures: int = 0, tenure_months: int = 0, api_key: str = "") -> str:
    """Predict churn risk for a customer"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    customer_data = {
        "last_login_days": last_login_days,
        "support_tickets_last_30d": support_tickets_last_30d,
        "nps_score": nps_score,
        "usage_decline_percent": usage_decline_percent,
        "payment_failures": payment_failures,
        "tenure_months": tenure_months,
    }

    result = calculate_risk_score(customer_data)
    prediction = {
        "id": create_id(),
        "customer_id": customer_id,
        "timestamp": datetime.now().isoformat(),
        **result,
    }
    _store["predictions"].append(prediction)

    if customer_id != "unknown":
        _store["customers"][customer_id] = {
            "last_prediction": prediction,
            "last_updated": datetime.now().isoformat(),
        }

    return json.dumps(prediction, indent=2)


@mcp.tool()
def batch_predict_churn(customers: list = None, api_key: str = "") -> str:
    """Predict churn for multiple customers"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    results = []
    for cust in (customers or []):
        result = calculate_risk_score(cust)
        results.append({"customer_id": cust.get("id"), **result})

    return json.dumps({"predictions": results, "count": len(results)}, indent=2)


@mcp.tool()
def get_customer_risk(customer_id: str, api_key: str = "") -> str:
    """Get current risk score for a customer"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if customer_id in _store["customers"]:
        return json.dumps(
            _store["customers"][customer_id]["last_prediction"], indent=2
        )
    return json.dumps({"error": "Customer not found"}, indent=2)


@mcp.tool()
def track_customer(customer_id: str, initial_data: dict = None, api_key: str = "") -> str:
    """Add customer to churn tracking"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    _store["customers"][customer_id] = {
        "initial_data": initial_data or {},
        "added_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
    }
    return json.dumps({"tracked": True, "customer_id": customer_id}, indent=2)


@mcp.tool()
def update_customer_signals(customer_id: str, signals: dict = None, api_key: str = "") -> str:
    """Update customer behavioral signals"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if customer_id not in _store["customers"]:
        return json.dumps({"error": "Customer not tracked"}, indent=2)

    _store["customers"][customer_id]["initial_data"].update(signals or {})
    _store["customers"][customer_id]["last_updated"] = datetime.now().isoformat()

    result = calculate_risk_score(_store["customers"][customer_id]["initial_data"])
    return json.dumps({"updated": True, "risk": result}, indent=2)


@mcp.tool()
def get_at_risk_customers(threshold: int = 60, limit: int = 50, api_key: str = "") -> str:
    """Get all customers above risk threshold"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    at_risk = []
    for cust_id, data in _store["customers"].items():
        pred = data.get("last_prediction", {})
        if pred.get("risk_score", 0) >= threshold:
            at_risk.append({"customer_id": cust_id, **pred})

    at_risk.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    return json.dumps(
        {"at_risk_customers": at_risk[:limit], "total": len(at_risk)}, indent=2
    )


@mcp.tool()
def create_retention_action(customer_id: str, action_type: str, description: str = "", api_key: str = "") -> str:
    """Create a retention action for at-risk customer"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    action = {
        "id": create_id(),
        "customer_id": customer_id,
        "type": action_type,
        "description": description,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    _store["retention_actions"].append(action)

    return json.dumps(
        {
            "action_created": True,
            "action_id": action["id"],
            "type": action["type"],
            "tip": f"Use get_retention_actions to track progress",
        },
        indent=2,
    )


@mcp.tool()
def get_retention_actions(customer_id: str = "", status: str = "", api_key: str = "") -> str:
    """Get retention actions for a customer"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    actions = _store["retention_actions"]
    if customer_id:
        actions = [a for a in actions if a.get("customer_id") == customer_id]
    if status:
        actions = [a for a in actions if a.get("status") == status]

    return json.dumps({"actions": actions}, indent=2)


@mcp.tool()
def update_retention_action(action_id: str, status: str, api_key: str = "") -> str:
    """Update status of retention action"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    for action in _store["retention_actions"]:
        if action["id"] == action_id:
            action["status"] = status
            action["updated_at"] = datetime.now().isoformat()
            return json.dumps({"updated": True, "action": action}, indent=2)

    return json.dumps({"error": "Action not found"}, indent=2)


@mcp.tool()
def get_churn_analytics(period: str = "30d", api_key: str = "") -> str:
    """Get overall churn analytics"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    predictions = _store["predictions"]

    if period == "7d":
        cutoff = datetime.now() - timedelta(days=7)
    elif period == "30d":
        cutoff = datetime.now() - timedelta(days=30)
    else:
        cutoff = datetime.now() - timedelta(days=90)

    recent = [
        p for p in predictions if datetime.fromisoformat(p["timestamp"]) >= cutoff
    ]

    if not recent:
        return json.dumps({"message": "No data for period"}, indent=2)

    avg_risk = sum(p["risk_score"] for p in recent) / len(recent)
    at_risk_count = sum(1 for p in recent if p["risk_score"] >= 60)

    return json.dumps(
        {
            "period": period,
            "total_predictions": len(recent),
            "average_risk_score": round(avg_risk, 1),
            "at_risk_count": at_risk_count,
            "at_risk_percent": round(at_risk_count / len(recent) * 100, 1),
            "critical_count": sum(1 for p in recent if p["risk_score"] >= 80),
        },
        indent=2,
    )


@mcp.tool()
def get_cohort_retention(cohort_month: str = "", api_key: str = "") -> str:
    """Get cohort retention analysis"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    return json.dumps(
        {
            "cohort": cohort_month,
            "note": "Cohort tracking requires ongoing data collection",
        },
        indent=2,
    )


@mcp.tool()
def simulate_intervention(customer_id: str, action_type: str = "", api_key: str = "") -> str:
    """Simulate impact of retention action"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if customer_id not in _store["customers"]:
        return json.dumps({"error": "Customer not found"}, indent=2)

    current_risk = (
        _store["customers"][customer_id]
        .get("last_prediction", {})
        .get("risk_score", 50)
    )

    impact_map = {
        "outreach": -15,
        "discount": -20,
        "upgrade": -10,
        "survey": -5,
        "bonus": -12,
    }

    impact = impact_map.get(action_type, -10)
    simulated_risk = max(0, current_risk + impact)

    return json.dumps(
        {
            "current_risk": current_risk,
            "simulated_risk": simulated_risk,
            "improvement": impact,
            "recommendation": "high_priority"
            if simulated_risk < current_risk and current_risk > 60
            else "standard",
        },
        indent=2,
    )


@mcp.tool()
def get_risk_trends(customer_id: str, days: int = 30, api_key: str = "") -> str:
    """Get risk score trends over time"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    predictions = [
        p for p in _store["predictions"] if p.get("customer_id") == customer_id
    ]

    cutoff = datetime.now() - timedelta(days=days)
    predictions = [
        p for p in predictions if datetime.fromisoformat(p["timestamp"]) >= cutoff
    ]

    if not predictions:
        return json.dumps({"message": "No trend data available"}, indent=2)

    return json.dumps(
        {
            "customer_id": customer_id,
            "trend": "improving"
            if predictions[-1]["risk_score"] < predictions[0]["risk_score"]
            else "worsening",
            "data_points": len(predictions),
            "earliest_risk": predictions[0]["risk_score"],
            "latest_risk": predictions[-1]["risk_score"],
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
