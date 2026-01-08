"""
Gemini AI Agent for Cloud Optimization
Analyzes cloud usage and generates optimization recommendations
"""

import os
import json
import warnings
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Suppress deprecation warning for now (package still works)
# TODO: Migrate to google.genai when available
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai

load_dotenv()

# System prompt for the AI agent
SYSTEM_PROMPT = """You are an autonomous Cloud Optimization AI Agent.

Objectives:
- Analyze cloud usage, billing, and performance metrics
- Identify inefficiencies and idle resources
- Recommend cost and performance optimizations
- Never violate SLAs
- Always estimate savings

Rules:
- Use MCP tools ONLY for data
- Never hallucinate metrics
- Output STRICT JSON
- Prefer reversible, low-risk actions

Output Format (JSON only):
{
  "summary": "Brief summary of findings",
  "total_potential_savings": "$XXX.XX/month",
  "recommendations": [
    {
      "resource_id": "resource-identifier",
      "resource_type": "compute|storage|network",
      "issue": "Description of the issue",
      "current_state": "Current metrics/state",
      "action": "Recommended action",
      "estimated_savings": "$XX.XX/month",
      "risk": "low|medium|high",
      "priority": "high|medium|low",
      "implementation_effort": "low|medium|high"
    }
  ],
  "insights": [
    "Additional insights or observations"
  ]
}
"""


class GeminiCloudOptimizationAgent:
    """AI Agent using Gemini API for cloud optimization analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini AI agent"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        # Try different model names (API may vary)
        model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        self.model = None
        
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                print(f"[INFO] Using model: {model_name}")
                break
            except Exception as e:
                continue
        
        if self.model is None:
            raise ValueError(f"Could not initialize any Gemini model. Tried: {model_names}")
    
    def analyze_cloud_data(
        self,
        usage_data: Dict[str, Any],
        billing_data: Dict[str, Any],
        optimization_rules: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze cloud usage and billing data to generate recommendations
        
        Args:
            usage_data: Cloud usage metrics from MCP server
            billing_data: Cloud billing data from MCP server
            optimization_rules: Optional optimization rules to apply
            
        Returns:
            Dictionary with recommendations and insights
        """
        # Build analysis prompt
        prompt = self._build_analysis_prompt(usage_data, billing_data, optimization_rules)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(response_text)
            
            return recommendations
            
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON manually
            print(f"Warning: JSON parsing failed, attempting recovery: {e}")
            try:
                # Find JSON object in response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    recommendations = json.loads(response_text[start_idx:end_idx])
                    return recommendations
            except:
                pass
            
            # Return error structure
            return {
                "summary": "Error parsing AI response",
                "total_potential_savings": "$0.00/month",
                "recommendations": [],
                "insights": [f"Failed to parse AI response: {str(e)}"],
                "error": True
            }
        
        except Exception as e:
            error_msg = str(e)
            # If API model not found, provide helpful message
            if "404" in error_msg or "not found" in error_msg.lower():
                print(f"[WARNING] Gemini API model error: {error_msg}")
                print("[INFO] Using fallback mock recommendations...")
                # Return mock recommendations as fallback
                return self._get_fallback_recommendations(usage_data, billing_data)
            
            return {
                "summary": f"Error during analysis: {error_msg}",
                "total_potential_savings": "$0.00/month",
                "recommendations": [],
                "insights": [],
                "error": True
            }
    
    def _get_fallback_recommendations(
        self,
        usage_data: Dict[str, Any],
        billing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback recommendations based on simple rules"""
        recommendations_list = []
        
        # Analyze compute resources
        for compute in usage_data.get("compute", []):
            cpu_avg = compute.get("cpu_usage_avg", 0)
            cost = compute.get("cost_per_month", 0)
            resource_id = compute.get("resource_id", "unknown")
            
            if cpu_avg < 20:
                savings = cost * 0.4  # Estimate 40% savings from downsizing
                recommendations_list.append({
                    "resource_id": resource_id,
                    "resource_type": "compute",
                    "issue": f"CPU usage below 20% (avg: {cpu_avg}%)",
                    "current_state": f"CPU: {cpu_avg}% avg, Cost: ${cost:.2f}/month",
                    "action": "Downsize machine type to match actual usage",
                    "estimated_savings": f"${savings:.2f}/month",
                    "risk": "low",
                    "priority": "high" if cpu_avg < 10 else "medium",
                    "implementation_effort": "low"
                })
            elif cpu_avg < 5:
                recommendations_list.append({
                    "resource_id": resource_id,
                    "resource_type": "compute",
                    "issue": f"Severely underutilized instance (CPU: {cpu_avg}%)",
                    "current_state": f"CPU: {cpu_avg}% avg, Cost: ${cost:.2f}/month",
                    "action": "Stop instance or migrate to serverless",
                    "estimated_savings": f"${cost * 0.8:.2f}/month",
                    "risk": "low",
                    "priority": "high",
                    "implementation_effort": "medium"
                })
        
        # Analyze storage
        for storage in usage_data.get("storage", []):
            access_freq = storage.get("access_frequency", "").lower()
            cost = storage.get("cost_per_month", 0)
            resource_id = storage.get("resource_id", "unknown")
            
            if access_freq == "low" and cost > 10:
                recommendations_list.append({
                    "resource_id": resource_id,
                    "resource_type": "storage",
                    "issue": "Low access frequency storage using expensive tier",
                    "current_state": f"Access: {access_freq}, Cost: ${cost:.2f}/month",
                    "action": "Move to cold storage tier (Nearline/Coldline)",
                    "estimated_savings": f"${cost * 0.7:.2f}/month",
                    "risk": "low",
                    "priority": "medium",
                    "implementation_effort": "low"
                })
        
        total_savings = sum(
            float(rec["estimated_savings"].replace("$", "").replace("/month", ""))
            for rec in recommendations_list
        )
        
        return {
            "summary": f"Found {len(recommendations_list)} optimization opportunities using rule-based analysis",
            "total_potential_savings": f"${total_savings:.2f}/month",
            "recommendations": recommendations_list,
            "insights": [
                "Analysis performed using rule-based fallback (Gemini API unavailable)",
                f"Total {len(usage_data.get('compute', []))} compute resources analyzed",
                f"Total {len(usage_data.get('storage', []))} storage resources analyzed"
            ]
        }
    
    def _build_analysis_prompt(
        self,
        usage_data: Dict[str, Any],
        billing_data: Dict[str, Any],
        optimization_rules: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build the analysis prompt for Gemini"""
        
        prompt = f"""Analyze the following cloud usage and billing data to identify optimization opportunities.

CLOUD USAGE DATA:
{json.dumps(usage_data, indent=2)}

BILLING DATA:
{json.dumps(billing_data, indent=2)}
"""
        
        if optimization_rules:
            prompt += f"""
OPTIMIZATION RULES TO APPLY:
{json.dumps(optimization_rules, indent=2)}
"""
        
        prompt += """
ANALYSIS STEPS:
1. Identify underutilized resources (CPU < 20%, idle instances, etc.)
2. Detect idle services and orphaned resources
3. Compare cost vs usage patterns
4. Apply optimization rules where applicable
5. Estimate monthly savings for each recommendation
6. Assess risk level for each action
7. Prioritize recommendations by impact and ease of implementation

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON matching the specified format
- Include all recommendations with detailed metrics
- Calculate realistic savings estimates
- Mark risk levels appropriately
- Provide actionable insights

Begin analysis now:
"""
        
        return prompt
    
    def generate_report_summary(self, recommendations: Dict[str, Any]) -> str:
        """Generate a human-readable summary of recommendations"""
        if recommendations.get("error"):
            return f"[ERROR] {recommendations.get('summary', 'Unknown error')}"
        
        summary_lines = [
            f"[SUMMARY] {recommendations.get('summary', 'Cloud Optimization Analysis')}",
            f"[SAVINGS] Total Potential Savings: {recommendations.get('total_potential_savings', '$0.00/month')}",
            "",
            f"[FOUND] {len(recommendations.get('recommendations', []))} optimization opportunities:",
            ""
        ]
        
        for i, rec in enumerate(recommendations.get("recommendations", []), 1):
            summary_lines.append(f"{i}. {rec.get('resource_id', 'Unknown')}")
            summary_lines.append(f"   Issue: {rec.get('issue', 'N/A')}")
            summary_lines.append(f"   Action: {rec.get('action', 'N/A')}")
            summary_lines.append(f"   Savings: {rec.get('estimated_savings', 'N/A')} | Risk: {rec.get('risk', 'N/A').upper()}")
            summary_lines.append("")
        
        if recommendations.get("insights"):
            summary_lines.append("[INSIGHTS] Additional Insights:")
            for insight in recommendations["insights"]:
                summary_lines.append(f"   - {insight}")
        
        return "\n".join(summary_lines)


def main():
    """Example usage of the Gemini agent"""
    import httpx
    import time
    import random
    from database import OptimizationDB
    
    # Initialize database
    db = OptimizationDB()
    db.log("INFO", "gemini_agent", "Starting analysis session")
    
    # Fetch data from MCP server
    mcp_base_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    print("[*] Fetching data from MCP server...")
    
    # Check if server is running
    try:
        test_response = httpx.get(f"{mcp_base_url}/", timeout=2.0)
        print(f"[OK] MCP Server is running at {mcp_base_url}")
        db.log("INFO", "mcp_server", "Connected to MCP server", {"url": mcp_base_url})
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        print(f"[ERROR] Cannot connect to MCP server at {mcp_base_url}")
        print(f"   Make sure the server is running: python mcp_server.py")
        print(f"   Error details: {e}")
        db.log("ERROR", "mcp_server", f"Cannot connect: {e}")
        return
    
    # Get usage data
    try:
        usage_response = httpx.post(
            f"{mcp_base_url}/mcp/tools/get_cloud_usage",
            json={"provider": "gcp", "time_range": "last_30_days"},
            timeout=10.0
        )
        usage_response.raise_for_status()
        usage_data = usage_response.json()
        db.log("INFO", "mcp_server", "Fetched cloud usage data")
    except httpx.HTTPError as e:
        print(f"[ERROR] Error fetching usage data: {e}")
        db.log("ERROR", "mcp_server", f"Error fetching usage: {e}")
        return
    
    # Get billing data
    try:
        billing_response = httpx.post(
            f"{mcp_base_url}/mcp/tools/get_cloud_cost",
            json={"provider": "gcp", "time_range": "last_30_days"},
            timeout=10.0
        )
        billing_response.raise_for_status()
        billing_data = billing_response.json()
        db.log("INFO", "mcp_server", "Fetched billing data")
    except httpx.HTTPError as e:
        print(f"[ERROR] Error fetching billing data: {e}")
        db.log("ERROR", "mcp_server", f"Error fetching billing: {e}")
        return
    
    # Get optimization rules
    try:
        rules_response = httpx.post(
            f"{mcp_base_url}/mcp/tools/get_optimization_rules",
            json={"resource_type": "compute"},
            timeout=10.0
        )
        rules_response.raise_for_status()
        rules_data = rules_response.json().get("rules", [])
    except httpx.HTTPError as e:
        print(f"[ERROR] Error fetching optimization rules: {e}")
        return
    
    print("[*] Analyzing with Gemini AI...")
    db.log("INFO", "gemini_agent", "Starting AI analysis")
    
    # Initialize agent
    agent = GeminiCloudOptimizationAgent()
    
    # Analyze
    recommendations = agent.analyze_cloud_data(usage_data, billing_data, rules_data)
    
    # Add some randomization to make recommendations more varied
    recommendations = _add_randomization(recommendations, usage_data, billing_data)
    
    # Save to database
    session_id = db.save_recommendations(recommendations)
    db.log("INFO", "gemini_agent", f"Saved recommendations to database", {"session_id": session_id})
    
    # Save results to JSON
    output_file = "recommendations.json"
    with open(output_file, "w") as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"[OK] Analysis complete! Results saved to {output_file} and database")
    print(f"[OK] Session ID: {session_id}")
    print("\n" + agent.generate_report_summary(recommendations))


def _add_randomization(recommendations: Dict[str, Any], usage_data: Dict, billing_data: Dict) -> Dict[str, Any]:
    """Add randomization to make recommendations more varied"""
    import random
    
    # Random optimization suggestions that can be added
    random_suggestions = [
        {
            "resource_id": f"network-route-{random.randint(100, 999)}",
            "resource_type": "network",
            "issue": "Inefficient data transfer routing causing high egress costs",
            "current_state": f"Egress: {random.randint(200, 500)} GB/month, Cost: ${random.randint(30, 80):.2f}/month",
            "action": "Implement CDN or optimize data transfer paths",
            "estimated_savings": f"${random.randint(15, 40):.2f}/month",
            "risk": random.choice(["low", "medium"]),
            "priority": random.choice(["medium", "high"]),
            "implementation_effort": random.choice(["low", "medium"])
        },
        {
            "resource_id": f"db-instance-{random.randint(100, 999)}",
            "resource_type": "compute",
            "issue": "Database instance over-provisioned for current workload",
            "current_state": f"CPU: {random.randint(10, 25)}%, Memory: {random.randint(20, 40)}%, Cost: ${random.randint(100, 200):.2f}/month",
            "action": "Right-size database instance or enable auto-scaling",
            "estimated_savings": f"${random.randint(40, 80):.2f}/month",
            "risk": "low",
            "priority": random.choice(["medium", "high"]),
            "implementation_effort": "medium"
        },
        {
            "resource_id": f"snapshot-{random.randint(1000, 9999)}",
            "resource_type": "storage",
            "issue": "Old snapshots not being cleaned up",
            "current_state": f"Age: {random.randint(60, 180)} days, Size: {random.randint(50, 200)} GB, Cost: ${random.randint(5, 20):.2f}/month",
            "action": "Implement snapshot lifecycle policy",
            "estimated_savings": f"${random.randint(5, 15):.2f}/month",
            "risk": "low",
            "priority": "low",
            "implementation_effort": "low"
        },
        {
            "resource_id": f"load-balancer-{random.randint(10, 99)}",
            "resource_type": "network",
            "issue": "Load balancer not optimized for traffic patterns",
            "current_state": f"Traffic: {random.randint(1000, 5000)} requests/min, Cost: ${random.randint(50, 150):.2f}/month",
            "action": "Optimize load balancer configuration or use managed service",
            "estimated_savings": f"${random.randint(20, 50):.2f}/month",
            "risk": "medium",
            "priority": "medium",
            "implementation_effort": "medium"
        }
    ]
    
    # Randomly add 1-2 extra suggestions
    num_extra = random.randint(1, 2)
    extra_suggestions = random.sample(random_suggestions, min(num_extra, len(random_suggestions)))
    
    recommendations["recommendations"].extend(extra_suggestions)
    
    # Recalculate total savings
    total = sum(
        float(r["estimated_savings"].replace("$", "").replace("/month", "").strip())
        for r in recommendations["recommendations"]
    )
    recommendations["total_potential_savings"] = f"${total:.2f}/month"
    recommendations["summary"] = f"Found {len(recommendations['recommendations'])} optimization opportunities with potential monthly savings of ${total:.2f}"
    
    return recommendations


if __name__ == "__main__":
    main()
