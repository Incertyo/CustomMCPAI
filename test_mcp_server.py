"""
Test script for MCP Server endpoints
"""

import httpx
import json
import time

MCP_BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all MCP server endpoints"""
    print("🧪 Testing MCP Server Endpoints")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = httpx.get(f"{MCP_BASE_URL}/")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure MCP server is running: python mcp_server.py")
        return
    
    # Test 2: List tools
    print("\n2. Testing /mcp/tools...")
    try:
        response = httpx.get(f"{MCP_BASE_URL}/mcp/tools")
        print(f"   ✅ Status: {response.status_code}")
        tools = response.json().get("tools", [])
        print(f"   Found {len(tools)} tools")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get cloud usage
    print("\n3. Testing /mcp/tools/get_cloud_usage...")
    try:
        response = httpx.post(
            f"{MCP_BASE_URL}/mcp/tools/get_cloud_usage",
            json={"provider": "gcp", "time_range": "last_30_days"}
        )
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Provider: {data.get('provider')}")
        print(f"   Compute resources: {len(data.get('compute', []))}")
        print(f"   Storage resources: {len(data.get('storage', []))}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get cloud cost
    print("\n4. Testing /mcp/tools/get_cloud_cost...")
    try:
        response = httpx.post(
            f"{MCP_BASE_URL}/mcp/tools/get_cloud_cost",
            json={"provider": "gcp", "time_range": "last_30_days"}
        )
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Total cost: ${data.get('total_cost', 0):.2f}")
        print(f"   Currency: {data.get('currency')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Get optimization rules
    print("\n5. Testing /mcp/tools/get_optimization_rules...")
    try:
        response = httpx.post(
            f"{MCP_BASE_URL}/mcp/tools/get_optimization_rules",
            json={"resource_type": "compute"}
        )
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Resource type: {data.get('resource_type')}")
        print(f"   Total rules: {data.get('total_rules')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Update context
    print("\n6. Testing /mcp/context (POST)...")
    try:
        test_context = {
            "usage": {"test": "data"},
            "billing": {"total_cost": 100.0}
        }
        response = httpx.post(
            f"{MCP_BASE_URL}/mcp/context",
            json=test_context
        )
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 7: Get context
    print("\n7. Testing /mcp/context (GET)...")
    try:
        response = httpx.get(f"{MCP_BASE_URL}/mcp/context")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Context timestamp: {data.get('timestamp')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)  # Give server time to start
    test_endpoints()
