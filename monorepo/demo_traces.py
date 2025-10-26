#!/usr/bin/env python3
"""
AI Agent Training - OpenTelemetry Demo Script
Generates realistic traces for demonstration purposes
"""

import asyncio
import httpx
import json
import random
import time
from typing import List, Dict, Any

# Demo scenarios to execute
DEMO_SCENARIOS = [
    {
        "name": "Data Processing Pipeline",
        "description": "Simulates an AI agent processing data through multiple tools",
        "steps": [
            {"tool": "http_fetch", "data": {"url": "https://jsonplaceholder.typicode.com/posts/1"}},
            {"tool": "db_query", "data": {"query": "SELECT * FROM users WHERE age > 25", "database": "default"}},
            {"tool": "file_ops", "data": {"operation": "write", "path": "processed_data.json", "content": '{"status": "processed", "timestamp": "2024-01-01T00:00:00Z"}'}},
            {"tool": "file_ops", "data": {"operation": "read", "path": "processed_data.json"}},
        ]
    },
    {
        "name": "Web Scraping Agent",
        "description": "AI agent that scrapes web data and stores results",
        "steps": [
            {"tool": "http_fetch", "data": {"url": "https://httpbin.org/json"}},
            {"tool": "file_ops", "data": {"operation": "mkdir", "path": "scraped_data"}},
            {"tool": "file_ops", "data": {"operation": "write", "path": "scraped_data/result.json", "content": '{"scraped": true}'}},
            {"tool": "db_query", "data": {"query": "SELECT COUNT(*) as total FROM users", "database": "default"}},
        ]
    },
    {
        "name": "Error Handling Demo",
        "description": "Demonstrates error handling and retry behavior",
        "steps": [
            {"tool": "http_fetch", "data": {"url": "https://httpbin.org/status/500"}},  # Will trigger retries
            {"tool": "db_query", "data": {"query": "SELECT * FROM nonexistent_table", "database": "default"}},  # Will fail
            {"tool": "file_ops", "data": {"operation": "read", "path": "nonexistent_file.txt"}},  # Will fail
            {"tool": "http_fetch", "data": {"url": "https://httpbin.org/json"}},  # Will succeed
        ]
    },
    {
        "name": "Concurrent Operations",
        "description": "Multiple operations running concurrently",
        "steps": [
            {"tool": "http_fetch", "data": {"url": "https://httpbin.org/delay/1"}},
            {"tool": "http_fetch", "data": {"url": "https://httpbin.org/delay/2"}},
            {"tool": "db_query", "data": {"query": "SELECT * FROM users LIMIT 5", "database": "default"}},
            {"tool": "file_ops", "data": {"operation": "list", "path": "."}},
        ]
    }
]

class DemoRunner:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_api_health(self) -> bool:
        """Check if the API is running"""
        try:
            response = await self.client.get(f"{self.api_base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ API health check failed: {e}")
            return False
    
    async def execute_tool(self, tool: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call"""
        endpoint = f"{self.api_base_url}/tools/{tool.replace('_', '-')}"
        
        try:
            response = await self.client.post(endpoint, json=data)
            result = response.json()
            
            # Add some artificial processing time for demo purposes
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            return {
                "tool": tool,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "result": result,
                "data": data
            }
        except Exception as e:
            return {
                "tool": tool,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data": data
            }
    
    async def run_scenario(self, scenario: Dict[str, Any], concurrent: bool = False) -> List[Dict[str, Any]]:
        """Run a complete scenario"""
        print(f"\n🚀 Running scenario: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        
        if concurrent:
            # Run all steps concurrently
            tasks = [
                self.execute_tool(step["tool"], step["data"])
                for step in scenario["steps"]
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run steps sequentially
            results = []
            for step in scenario["steps"]:
                result = await self.execute_tool(step["tool"], step["data"])
                results.append(result)
                
                # Print progress
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {step['tool']}: {result.get('status_code', 'N/A')}")
        
        return results
    
    async def run_demo(self, scenarios: List[str] = None, concurrent: bool = False):
        """Run the complete demo"""
        print("🎯 AI Agent Training - OpenTelemetry Demo")
        print("=" * 50)
        
        # Check API health
        if not await self.check_api_health():
            print("❌ API is not running. Please start the API first:")
            print("   cd apps/api && ./run.sh")
            return
        
        print("✅ API is running and healthy")
        
        # Filter scenarios if specified
        demo_scenarios = DEMO_SCENARIOS
        if scenarios:
            demo_scenarios = [s for s in DEMO_SCENARIOS if s["name"] in scenarios]
        
        all_results = []
        
        for scenario in demo_scenarios:
            try:
                results = await self.run_scenario(scenario, concurrent)
                all_results.extend(results)
                
                # Summary
                successful = sum(1 for r in results if r.get("success", False))
                total = len(results)
                print(f"📊 Scenario completed: {successful}/{total} successful")
                
                # Wait between scenarios
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Scenario failed: {e}")
        
        # Overall summary
        print("\n" + "=" * 50)
        print("📈 Demo Summary")
        total_calls = len(all_results)
        successful_calls = sum(1 for r in all_results if r.get("success", False))
        print(f"Total tool calls: {total_calls}")
        print(f"Successful calls: {successful_calls}")
        print(f"Success rate: {successful_calls/total_calls*100:.1f}%")
        
        # Tool breakdown
        tool_stats = {}
        for result in all_results:
            tool = result.get("tool", "unknown")
            if tool not in tool_stats:
                tool_stats[tool] = {"total": 0, "success": 0}
            tool_stats[tool]["total"] += 1
            if result.get("success", False):
                tool_stats[tool]["success"] += 1
        
        print("\n🔧 Tool Statistics:")
        for tool, stats in tool_stats.items():
            success_rate = stats["success"] / stats["total"] * 100
            print(f"  {tool}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n🎯 Check traces in Jaeger UI: http://localhost:16686")
        print(f"🎯 Check metrics in Grafana: http://localhost:3001 (admin/admin)")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Agent Training OpenTelemetry Demo")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run")
    parser.add_argument("--concurrent", action="store_true", help="Run scenario steps concurrently")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat the demo")
    
    args = parser.parse_args()
    
    runner = DemoRunner(args.api_url)
    
    try:
        for i in range(args.repeat):
            if args.repeat > 1:
                print(f"\n🔄 Demo run {i+1}/{args.repeat}")
            
            await runner.run_demo(args.scenarios, args.concurrent)
            
            if i < args.repeat - 1:
                print(f"\n⏳ Waiting 5 seconds before next run...")
                await asyncio.sleep(5)
    
    finally:
        await runner.close()

if __name__ == "__main__":
    asyncio.run(main())
