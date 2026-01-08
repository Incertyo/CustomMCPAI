"""
MCP Server for Cloud Optimization AI Agent
Exposes tools for cloud usage, billing, and optimization rules
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Cloud Optimization MCP Server")

# Mock data storage (in production, connect to real cloud APIs)
MOCK_USAGE_DATA = {}
MOCK_BILLING_DATA = {}
MOCK_OPTIMIZATION_RULES = {
    "compute": [
        {
            "rule_id": "cpu_underutilization",
            "condition": "cpu_usage < 20",
            "recommendation": "Downsize VM instance",
            "risk_level": "low",
            "estimated_savings_percentage": 30
        },
        {
            "rule_id": "idle_instance",
            "condition": "cpu_usage < 5 AND network_egress < 1MB",
            "recommendation": "Stop or terminate idle instance",
            "risk_level": "medium",
            "estimated_savings_percentage": 100
        },
        {
            "rule_id": "reserved_instance_eligible",
            "condition": "constant_load AND uptime > 80%",
            "recommendation": "Purchase reserved instance",
            "risk_level": "low",
            "estimated_savings_percentage": 40
        }
    ],
    "storage": [
        {
            "rule_id": "cold_storage_eligible",
            "condition": "access_frequency < 1_per_month",
            "recommendation": "Move to cold storage tier",
            "risk_level": "low",
            "estimated_savings_percentage": 70
        },
        {
            "rule_id": "orphaned_snapshots",
            "condition": "snapshot_age > 90_days AND no_attached_volumes",
            "recommendation": "Delete orphaned snapshots",
            "risk_level": "low",
            "estimated_savings_percentage": 100
        }
    ],
    "network": [
        {
            "rule_id": "high_egress_cost",
            "condition": "egress_cost > 30%_of_total",
            "recommendation": "Optimize data transfer routing",
            "risk_level": "medium",
            "estimated_savings_percentage": 25
        }
    ]
}


class CloudUsageRequest(BaseModel):
    provider: str  # gcp, aws, azure
    time_range: str = "last_30_days"
    resource_type: Optional[str] = None


class CloudCostRequest(BaseModel):
    provider: str
    time_range: str = "last_30_days"


class OptimizationRulesRequest(BaseModel):
    resource_type: str  # compute, storage, network


class MCPContextRequest(BaseModel):
    usage: Dict[str, Any]
    billing: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    return {
        "service": "Cloud Optimization MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "tools": "/mcp/tools",
            "cloud_usage": "/mcp/tools/get_cloud_usage",
            "cloud_cost": "/mcp/tools/get_cloud_cost",
            "optimization_rules": "/mcp/tools/get_optimization_rules",
            "context": "/mcp/context"
        }
    }


@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_cloud_usage",
                "description": "Fetch compute, storage, and network usage metrics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": ["gcp", "aws", "azure"],
                            "description": "Cloud provider"
                        },
                        "time_range": {
                            "type": "string",
                            "default": "last_30_days",
                            "description": "Time range for data"
                        },
                        "resource_type": {
                            "type": "string",
                            "enum": ["compute", "storage", "network", None],
                            "description": "Optional resource type filter"
                        }
                    },
                    "required": ["provider"]
                }
            },
            {
                "name": "get_cloud_cost",
                "description": "Fetch cost and billing breakdown",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": ["gcp", "aws", "azure"],
                            "description": "Cloud provider"
                        },
                        "time_range": {
                            "type": "string",
                            "default": "last_30_days",
                            "description": "Time range for data"
                        }
                    },
                    "required": ["provider"]
                }
            },
            {
                "name": "get_optimization_rules",
                "description": "Get cloud best-practice optimization rules",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "enum": ["compute", "storage", "network"],
                            "description": "Resource type"
                        }
                    },
                    "required": ["resource_type"]
                }
            }
        ]
    }


@app.post("/mcp/tools/get_cloud_usage")
async def get_cloud_usage(request: CloudUsageRequest):
    """Fetch cloud usage metrics"""
    # In production, this would call actual cloud APIs
    # For now, return mock data with realistic structure
    
    end_date = datetime.now()
    if request.time_range == "last_30_days":
        start_date = end_date - timedelta(days=30)
    elif request.time_range == "last_7_days":
        start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Mock usage data
    mock_data = {
        "provider": request.provider,
        "time_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "compute": [
            {
                "resource_id": f"vm-prod-{request.provider}-01",
                "instance_type": "n1-standard-4",
                "region": "us-central1",
                "cpu_usage_avg": 15.5,
                "cpu_usage_max": 45.2,
                "memory_usage_avg": 32.1,
                "network_egress_gb": 125.3,
                "uptime_percentage": 99.8,
                "cost_per_month": 150.00
            },
            {
                "resource_id": f"vm-dev-{request.provider}-02",
                "instance_type": "n1-standard-2",
                "region": "us-east1",
                "cpu_usage_avg": 3.2,
                "cpu_usage_max": 8.5,
                "memory_usage_avg": 12.5,
                "network_egress_gb": 2.1,
                "uptime_percentage": 45.2,
                "cost_per_month": 75.00
            },
            {
                "resource_id": f"vm-staging-{request.provider}-03",
                "instance_type": "n1-standard-8",
                "region": "us-west1",
                "cpu_usage_avg": 65.8,
                "cpu_usage_max": 92.3,
                "memory_usage_avg": 78.5,
                "network_egress_gb": 450.2,
                "uptime_percentage": 100.0,
                "cost_per_month": 300.00
            }
        ],
        "storage": [
            {
                "resource_id": f"bucket-{request.provider}-data-01",
                "storage_type": "standard",
                "size_gb": 1250.5,
                "access_frequency": "high",
                "cost_per_month": 25.50
            },
            {
                "resource_id": f"bucket-{request.provider}-archive-02",
                "storage_type": "standard",
                "size_gb": 850.2,
                "access_frequency": "low",
                "cost_per_month": 17.00
            }
        ],
        "network": {
            "total_egress_gb": 577.6,
            "total_ingress_gb": 1200.3,
            "cost_per_month": 45.20
        }
    }
    
    # Filter by resource_type if specified
    if request.resource_type:
        if request.resource_type == "compute":
            return {"provider": request.provider, "compute": mock_data["compute"]}
        elif request.resource_type == "storage":
            return {"provider": request.provider, "storage": mock_data["storage"]}
        elif request.resource_type == "network":
            return {"provider": request.provider, "network": mock_data["network"]}
    
    return mock_data


@app.post("/mcp/tools/get_cloud_cost")
async def get_cloud_cost(request: CloudCostRequest):
    """Fetch cloud cost and billing breakdown"""
    end_date = datetime.now()
    if request.time_range == "last_30_days":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Mock billing data
    mock_billing = {
        "provider": request.provider,
        "time_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_cost": 612.70,
        "currency": "USD",
        "breakdown": {
            "compute": {
                "cost": 525.00,
                "percentage": 85.7,
                "resources": 3
            },
            "storage": {
                "cost": 42.50,
                "percentage": 6.9,
                "resources": 2
            },
            "network": {
                "cost": 45.20,
                "percentage": 7.4
            }
        },
        "trend": {
            "previous_period_cost": 650.00,
            "change_percentage": -5.7,
            "change_direction": "decreasing"
        },
        "top_cost_drivers": [
            {
                "resource_id": "vm-staging-gcp-03",
                "cost": 300.00,
                "category": "compute"
            },
            {
                "resource_id": "vm-prod-gcp-01",
                "cost": 150.00,
                "category": "compute"
            },
            {
                "resource_id": "network-egress",
                "cost": 45.20,
                "category": "network"
            }
        ]
    }
    
    return mock_billing


@app.post("/mcp/tools/get_optimization_rules")
async def get_optimization_rules(request: OptimizationRulesRequest):
    """Get optimization rules for a specific resource type"""
    if request.resource_type not in MOCK_OPTIMIZATION_RULES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resource_type. Must be one of: {list(MOCK_OPTIMIZATION_RULES.keys())}"
        )
    
    return {
        "resource_type": request.resource_type,
        "rules": MOCK_OPTIMIZATION_RULES[request.resource_type],
        "total_rules": len(MOCK_OPTIMIZATION_RULES[request.resource_type])
    }


@app.post("/mcp/context")
async def update_context(request: MCPContextRequest):
    """Update MCP context with usage and billing data"""
    # Store context for AI agent to access
    global MOCK_USAGE_DATA, MOCK_BILLING_DATA
    
    MOCK_USAGE_DATA = request.usage
    MOCK_BILLING_DATA = request.billing
    
    return {
        "status": "success",
        "message": "Context updated successfully",
        "timestamp": datetime.now().isoformat(),
        "usage_resources": len(request.usage.get("compute", [])) if "compute" in request.usage else 0,
        "billing_total": request.billing.get("total_cost", 0)
    }


@app.get("/mcp/context")
async def get_context():
    """Get current MCP context"""
    return {
        "usage": MOCK_USAGE_DATA,
        "billing": MOCK_BILLING_DATA,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    
    print(f"🚀 Starting MCP Server on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)
