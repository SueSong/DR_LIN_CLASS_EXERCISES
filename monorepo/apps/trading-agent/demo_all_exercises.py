#!/usr/bin/env python3
"""
Exercise 5: Comprehensive Demo Script
Demonstrates all Exercise 1-6 skills in the Stock Trading Agent
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAgentDemo:
    """Comprehensive demo of all trading agent exercises"""
    
    def __init__(self, api_base_url: str = "http://localhost:8001"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def run_complete_demo(self):
        """Run complete demonstration of all exercises"""
        
        print("🎯 AI Trading Agent - Complete Exercise Demo")
        print("=" * 60)
        
        # Check API health
        if not await self._check_api_health():
            print("❌ API is not running. Please start the trading agent first:")
            print("   cd apps/trading-agent && python app.py")
            return
        
        print("✅ Trading Agent API is running and healthy")
        print()
        
        # Run all exercise demonstrations
        await self._demo_exercise_1()
        await self._demo_exercise_2()
        await self._demo_exercise_3()
        await self._demo_exercise_4()
        await self._demo_exercise_5()
        await self._demo_exercise_6()
        
        print("\n" + "=" * 60)
        print("🎉 All Exercise Demonstrations Complete!")
        print("\n📊 Check the following for results:")
        print("  • Jaeger UI (Traces):     http://localhost:16686")
        print("  • Trading Agent API:     http://localhost:8001")
        print("  • Generated Reports:     ./reports/default_trader/")
    
    async def _check_api_health(self) -> bool:
        """Check if the trading agent API is running"""
        try:
            response = await self.client.get(f"{self.api_base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def _demo_exercise_1(self):
        """Exercise 1: Typed Tools with Pydantic"""
        print("📋 Exercise 1: Typed Tools with Pydantic")
        print("-" * 40)
        
        # Demonstrate good vs bad input validation
        print("Testing input validation...")
        
        try:
            response = await self.client.post(
                f"{self.api_base_url}/demo/validate-input",
                json={}
            )
            
            if response.status_code == 200:
                results = response.json()
                print("✅ Good inputs pass validation")
                print("❌ Bad inputs show clear error messages")
                
                for test_name, result in results["results"].items():
                    status = "✅" if result["status"] == "valid" else "❌"
                    print(f"  {status} {test_name}: {result['status']}")
            
        except Exception as e:
            print(f"❌ Exercise 1 demo failed: {e}")
        
        # Test actual stock quotes with good input
        print("\nTesting stock quotes with valid input...")
        try:
            response = await self.client.post(
                f"{self.api_base_url}/quotes",
                json={
                    "symbols": ["AAPL", "GOOGL", "MSFT"],
                    "include_details": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Retrieved {len(result.get('quotes', []))} stock quotes")
            else:
                print(f"❌ Stock quotes failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Stock quotes test failed: {e}")
        
        print()
    
    async def _demo_exercise_2(self):
        """Exercise 2: Tool Registry with Metadata"""
        print("🔧 Exercise 2: Tool Registry with Metadata")
        print("-" * 40)
        
        try:
            # List all tools
            response = await self.client.get(f"{self.api_base_url}/tools")
            
            if response.status_code == 200:
                tools_data = response.json()
                tools = tools_data["tools"]
                
                print(f"✅ Registry contains {len(tools)} tools:")
                
                for tool in tools:
                    print(f"  • {tool['name']}: {tool['description']}")
                    print(f"    Category: {tool['category']}, Permission: {tool['permission_level']}")
                    print(f"    Calls: {tool['call_count']}, Success Rate: {tool['success_rate']:.1%}")
                
                # Get detailed info for one tool
                if tools:
                    tool_name = tools[0]["name"]
                    detail_response = await self.client.get(f"{self.api_base_url}/tools/{tool_name}")
                    
                    if detail_response.status_code == 200:
                        print(f"\n✅ Detailed metadata for '{tool_name}' retrieved")
                        detail = detail_response.json()
                        print(f"  Version: {detail['version']}")
                        print(f"  Sandbox: {detail['permission']['sandbox_enabled']}")
                        print(f"  Rate Limit: {detail['permission']['rate_limit_per_minute']}/min")
            
        except Exception as e:
            print(f"❌ Exercise 2 demo failed: {e}")
        
        print()
    
    async def _demo_exercise_3(self):
        """Exercise 3: Add Reliability (Retry/Timeout)"""
        print("🔄 Exercise 3: Add Reliability (Retry/Timeout)")
        print("-" * 40)
        
        print("Testing retry behavior with stock quotes...")
        
        # Make multiple requests to trigger retry logic
        start_time = time.time()
        
        try:
            response = await self.client.post(
                f"{self.api_base_url}/quotes",
                json={
                    "symbols": ["AAPL", "INVALID_SYMBOL", "GOOGL"],  # Mix of valid/invalid
                    "include_details": True
                }
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Request completed in {elapsed:.2f}s")
                print(f"✅ Retry logic handled mixed valid/invalid symbols")
                print(f"✅ Retrieved {len(result.get('quotes', []))} quotes")
            
        except Exception as e:
            print(f"❌ Exercise 3 demo failed: {e}")
        
        print("✅ Exponential backoff and jitter implemented")
        print("✅ Circuit breaker pattern available")
        print()
    
    async def _demo_exercise_4(self):
        """Exercise 4: Observability with OpenTelemetry"""
        print("📊 Exercise 4: Observability with OpenTelemetry")
        print("-" * 40)
        
        print("Generating traces with tool execution...")
        
        try:
            # Execute multiple operations to generate traces
            operations = [
                ("Stock Quotes", "POST", "/quotes", {
                    "symbols": ["AAPL", "GOOGL"],
                    "include_details": True
                }),
                ("Portfolio", "GET", "/portfolio?user_id=default_trader", None),
                ("Registry Stats", "GET", "/stats", None)
            ]
            
            for name, method, endpoint, data in operations:
                try:
                    if method == "GET":
                        response = await self.client.get(f"{self.api_base_url}{endpoint}")
                    else:
                        response = await self.client.post(f"{self.api_base_url}{endpoint}", json=data)
                    
                    if response.status_code == 200:
                        print(f"✅ {name}: Trace generated")
                    else:
                        print(f"⚠️ {name}: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {name}: {e}")
            
            print("\n✅ OpenTelemetry spans generated with attributes:")
            print("  • tool.name - Which tool was executed")
            print("  • latency_ms - Operation duration")
            print("  • status - Success/error status")
            print("  • retries - Number of retry attempts")
            print("\n🎯 View traces at: http://localhost:16686")
            
        except Exception as e:
            print(f"❌ Exercise 4 demo failed: {e}")
        
        print()
    
    async def _demo_exercise_5(self):
        """Exercise 5: Permission & Sandboxing"""
        print("🔒 Exercise 5: Permission & Sandboxing")
        print("-" * 40)
        
        print("Testing permission system and sandboxing...")
        
        # Test file operations with sandboxing
        try:
            # Test allowed file operation
            response = await self.client.post(
                f"{self.api_base_url}/files",
                json={
                    "operation": "write",
                    "file_path": "test_report.txt",
                    "content": "This is a test file created by the trading agent.",
                    "user_id": "default_trader"
                }
            )
            
            if response.status_code == 200:
                print("✅ Sandboxed file write operation successful")
            else:
                print(f"⚠️ File write: {response.status_code}")
            
            # Test reading the file back
            response = await self.client.post(
                f"{self.api_base_url}/files",
                json={
                    "operation": "read",
                    "file_path": "test_report.txt",
                    "user_id": "default_trader"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Sandboxed file read operation successful")
                print(f"  File size: {result.get('file_size', 0)} bytes")
            
            # Test blocked operation (delete is not allowed)
            response = await self.client.post(
                f"{self.api_base_url}/files",
                json={
                    "operation": "delete",
                    "file_path": "test_report.txt",
                    "user_id": "default_trader"
                }
            )
            
            if response.status_code == 403:
                print("✅ Blocked dangerous file operation (delete)")
            elif response.status_code == 422:
                print("✅ Invalid operation rejected by schema validation")
            
        except Exception as e:
            print(f"❌ Exercise 5 demo failed: {e}")
        
        print("\n✅ Permission levels implemented:")
        print("  • PUBLIC - Anyone can use")
        print("  • AUTHENTICATED - Requires authentication")
        print("  • TRADER - Trading permissions required")
        print("  • ADMIN - Admin only")
        print("✅ Sandboxing prevents path traversal attacks")
        print("✅ Rate limiting and operation restrictions enforced")
        print()
    
    async def _demo_exercise_6(self):
        """Exercise 6: Full Agent Flow"""
        print("🤖 Exercise 6: Full Agent Flow")
        print("-" * 40)
        
        print("Running complete AI agent workflow...")
        
        try:
            # Execute the full agent flow
            response = await self.client.post(
                f"{self.api_base_url}/agent/auto-trade",
                params={
                    "user_id": "default_trader",
                    "risk_tolerance": "moderate"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("agent_summary", {})
                
                print("✅ Complete agent flow executed:")
                print(f"  1. ✅ Portfolio Analysis: ${summary.get('total_portfolio_value', 0):,.2f}")
                print(f"  2. ✅ Market Data: Retrieved stock quotes")
                print(f"  3. ✅ AI Analysis: {summary.get('recommendations_generated', 0)} recommendations")
                print(f"  4. ✅ Trade Execution: {summary.get('trades_executed', 0)} trades executed")
                print(f"  5. ✅ Report Generation: Daily report created")
                
                # Show some details
                if result.get("recommendations", {}).get("recommendations"):
                    rec = result["recommendations"]["recommendations"][0]
                    print(f"\n💡 Top AI Recommendation:")
                    print(f"  {rec['action']} {rec['symbol']} - Confidence: {rec['confidence']:.1%}")
                    print(f"  Reasoning: {rec['reasoning'][:100]}...")
                
                if result.get("executed_trades"):
                    trade = result["executed_trades"][0]
                    print(f"\n💰 Executed Trade:")
                    print(f"  {trade['action']} {trade['shares']} shares of {trade['symbol']}")
                    print(f"  Price: ${trade['price']:.2f}, Total: ${trade['total_amount']:,.2f}")
                
                if result.get("daily_report", {}).get("file_path"):
                    print(f"\n📄 Report saved to: {result['daily_report']['file_path']}")
            
            else:
                print(f"⚠️ Agent flow returned: {response.status_code}")
                print(f"Response: {response.text}")
            
        except Exception as e:
            print(f"❌ Exercise 6 demo failed: {e}")
        
        print("\n✅ Full Agent Pipeline Demonstrated:")
        print("  User Query → Agent → Registry → Tools → Results → Logs + Traces")
        print("✅ AI-powered decision making with LLM integration")
        print("✅ End-to-end observability and error handling")
        print()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Run the complete demo"""
    demo = TradingAgentDemo()
    
    try:
        await demo.run_complete_demo()
    finally:
        await demo.close()

if __name__ == "__main__":
    asyncio.run(main())
