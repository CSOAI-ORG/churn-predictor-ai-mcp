#!/usr/bin/env python3
"""MEOK AI Labs — churn-predictor-ai-mcp MCP Server. Comprehensive customer churn prediction and retention analytics."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any
import uuid
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

_store = {"customers": {}, "predictions": [], "retention_actions": [], "cohorts": {}}

server = Server("churn-predictor-ai-mcp")


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


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return [
        Resource(
            uri="churn://customers",
            name="Customer Risk List",
            description="All customers with risk scores",
            mimeType="application/json",
        ),
        Resource(
            uri="churn://predictions",
            name="Churn Predictions",
            description="Historical predictions",
            mimeType="application/json",
        ),
        Resource(
            uri="churn://cohorts",
            name="Cohort Analysis",
            description="Cohort retention data",
            mimeType="application/json",
        ),
    ]


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="predict_churn",
            description="Predict churn risk for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "last_login_days": {"type": "number"},
                    "support_tickets_last_30d": {"type": "number"},
                    "nps_score": {"type": "number"},
                    "usage_decline_percent": {"type": "number"},
                    "payment_failures": {"type": "number"},
                    "tenure_months": {"type": "number"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="batch_predict_churn",
            description="Predict churn for multiple customers",
            inputSchema={
                "type": "object",
                "properties": {
                    "customers": {"type": "array"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_customer_risk",
            description="Get current risk score for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="track_customer",
            description="Add customer to churn tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "initial_data": {"type": "object"},
                },
                "required": ["customer_id"],
            },
        ),
        Tool(
            name="update_customer_signals",
            description="Update customer behavioral signals",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "signals": {"type": "object"},
                },
                "required": ["customer_id", "signals"],
            },
        ),
        Tool(
            name="get_at_risk_customers",
            description="Get all customers above risk threshold",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold": {"type": "number"},
                    "limit": {"type": "number"},
                },
            },
        ),
        Tool(
            name="create_retention_action",
            description="Create a retention action for at-risk customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "action_type": {
                        "type": "string",
                        "enum": ["outreach", "discount", "upgrade", "survey", "bonus"],
                    },
                    "description": {"type": "string"},
                    "api_key": {"type": "string"},
                },
                "required": ["customer_id", "action_type"],
            },
        ),
        Tool(
            name="get_retention_actions",
            description="Get retention actions for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
        ),
        Tool(
            name="update_retention_action",
            description="Update status of retention action",
            inputSchema={
                "type": "object",
                "properties": {
                    "action_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "failed"],
                    },
                },
                "required": ["action_id", "status"],
            },
        ),
        Tool(
            name="get_churn_analytics",
            description="Get overall churn analytics",
            inputSchema={
                "type": "object",
                "properties": {"period": {"type": "string"}},
                "default": {"period": "30d"},
            },
        ),
        Tool(
            name="get_cohort_retention",
            description="Get cohort retention analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "cohort_month": {"type": "string"},
                    "api_key": {"type": "string"},
                },
            },
        ),
        Tool(
            name="simulate_intervention",
            description="Simulate impact of retention action",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "action_type": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_risk_trends",
            description="Get risk score trends over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "days": {"type": "number"},
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent]:
    args = arguments or {}
    api_key = args.get("api_key", "")

    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
                ),
            )
        ]

    if name == "predict_churn":
        customer_data = {
            "last_login_days": args.get("last_login_days", 0),
            "support_tickets_last_30d": args.get("support_tickets_last_30d", 0),
            "nps_score": args.get("nps_score", 5),
            "usage_decline_percent": args.get("usage_decline_percent", 0),
            "payment_failures": args.get("payment_failures", 0),
            "tenure_months": args.get("tenure_months", 0),
        }

        result = calculate_risk_score(customer_data)
        prediction = {
            "id": create_id(),
            "customer_id": args.get("customer_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            **result,
        }
        _store["predictions"].append(prediction)

        if args.get("customer_id"):
            _store["customers"][args["customer_id"]] = {
                "last_prediction": prediction,
                "last_updated": datetime.now().isoformat(),
            }

        return [TextContent(type="text", text=json.dumps(prediction, indent=2))]

    elif name == "batch_predict_churn":
        results = []
        for cust in args.get("customers", []):
            result = calculate_risk_score(cust)
            results.append({"customer_id": cust.get("id"), **result})

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"predictions": results, "count": len(results)}, indent=2
                ),
            )
        ]

    elif name == "get_customer_risk":
        customer_id = args.get("customer_id")
        if customer_id in _store["customers"]:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        _store["customers"][customer_id]["last_prediction"], indent=2
                    ),
                )
            ]
        return [
            TextContent(
                type="text", text=json.dumps({"error": "Customer not found"}, indent=2)
            )
        ]

    elif name == "track_customer":
        customer_id = args["customer_id"]
        _store["customers"][customer_id] = {
            "initial_data": args.get("initial_data", {}),
            "added_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"tracked": True, "customer_id": customer_id}, indent=2
                ),
            )
        ]

    elif name == "update_customer_signals":
        customer_id = args["customer_id"]
        if customer_id not in _store["customers"]:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": "Customer not tracked"}, indent=2),
                )
            ]

        _store["customers"][customer_id]["initial_data"].update(args.get("signals", {}))
        _store["customers"][customer_id]["last_updated"] = datetime.now().isoformat()

        result = calculate_risk_score(_store["customers"][customer_id]["initial_data"])
        return [
            TextContent(
                type="text",
                text=json.dumps({"updated": True, "risk": result}, indent=2),
            )
        ]

    elif name == "get_at_risk_customers":
        threshold = args.get("threshold", 60)
        limit = args.get("limit", 50)

        at_risk = []
        for cust_id, data in _store["customers"].items():
            pred = data.get("last_prediction", {})
            if pred.get("risk_score", 0) >= threshold:
                at_risk.append({"customer_id": cust_id, **pred})

        at_risk.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"at_risk_customers": at_risk[:limit], "total": len(at_risk)},
                    indent=2,
                ),
            )
        ]

    elif name == "create_retention_action":
        action = {
            "id": create_id(),
            "customer_id": args["customer_id"],
            "type": args["action_type"],
            "description": args.get("description", ""),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        _store["retention_actions"].append(action)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "action_created": True,
                        "action_id": action["id"],
                        "type": action["type"],
                        "tip": f"Use get_retention_actions to track progress",
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_retention_actions":
        customer_id = args.get("customer_id")
        status = args.get("status")

        actions = _store["retention_actions"]
        if customer_id:
            actions = [a for a in actions if a.get("customer_id") == customer_id]
        if status:
            actions = [a for a in actions if a.get("status") == status]

        return [
            TextContent(type="text", text=json.dumps({"actions": actions}, indent=2))
        ]

    elif name == "update_retention_action":
        action_id = args["action_id"]
        status = args["status"]

        for action in _store["retention_actions"]:
            if action["id"] == action_id:
                action["status"] = status
                action["updated_at"] = datetime.now().isoformat()
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"updated": True, "action": action}, indent=2),
                    )
                ]

        return [
            TextContent(
                type="text", text=json.dumps({"error": "Action not found"}, indent=2)
            )
        ]

    elif name == "get_churn_analytics":
        predictions = _store["predictions"]
        period = args.get("period", "30d")

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
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"message": "No data for period"}, indent=2),
                )
            ]

        avg_risk = sum(p["risk_score"] for p in recent) / len(recent)
        at_risk_count = sum(1 for p in recent if p["risk_score"] >= 60)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "period": period,
                        "total_predictions": len(recent),
                        "average_risk_score": round(avg_risk, 1),
                        "at_risk_count": at_risk_count,
                        "at_risk_percent": round(at_risk_count / len(recent) * 100, 1),
                        "critical_count": sum(
                            1 for p in recent if p["risk_score"] >= 80
                        ),
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_cohort_retention":
        cohort_month = args.get("cohort_month")
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "cohort": cohort_month,
                        "note": "Cohort tracking requires ongoing data collection",
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "simulate_intervention":
        customer_id = args.get("customer_id")
        action_type = args.get("action_type")

        if customer_id not in _store["customers"]:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": "Customer not found"}, indent=2),
                )
            ]

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

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "current_risk": current_risk,
                        "simulated_risk": simulated_risk,
                        "improvement": impact,
                        "recommendation": "high_priority"
                        if simulated_risk < current_risk and current_risk > 60
                        else "standard",
                    },
                    indent=2,
                ),
            )
        ]

    elif name == "get_risk_trends":
        customer_id = args.get("customer_id")
        days = args.get("days", 30)

        predictions = [
            p for p in _store["predictions"] if p.get("customer_id") == customer_id
        ]

        cutoff = datetime.now() - timedelta(days=days)
        predictions = [
            p for p in predictions if datetime.fromisoformat(p["timestamp"]) >= cutoff
        ]

        if not predictions:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"message": "No trend data available"}, indent=2),
                )
            ]

        return [
            TextContent(
                type="text",
                text=json.dumps(
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
                ),
            )
        ]

    return [
        TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))
    ]


async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (
        read_stream,
        write_stream,
    ):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="churn-predictor-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
