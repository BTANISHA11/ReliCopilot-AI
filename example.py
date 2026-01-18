#!/usr/bin/env python3
"""
Example script demonstrating ReliCopilot-AI API usage.
"""

import asyncio
import httpx
from datetime import datetime

API_BASE_URL = "http://localhost:8000"


async def main():
    """Run example demonstrations."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("🛡️  ReliCopilot-AI API Examples\n")
        
        # 1. Check health
        print("1. Health Check")
        response = await client.get(f"{API_BASE_URL}/health")
        print(f"   Status: {response.json()['status']}")
        print()
        
        # 2. Get initial stats
        print("2. Current Statistics")
        response = await client.get(f"{API_BASE_URL}/api/stats")
        stats = response.json()
        print(f"   Total Events: {stats['total_events']}")
        print(f"   Error Count: {stats['error_count']}")
        print(f"   Error Rate: {stats['error_rate_percent']}%")
        print(f"   Avg Latency: {stats['avg_latency_ms']:.2f} ms")
        print()
        
        # 3. Trigger some simulated requests
        print("3. Simulating 5 requests (some may fail)...")
        successes = 0
        failures = 0
        
        for i in range(5):
            try:
                response = await client.get(f"{API_BASE_URL}/api/simulate")
                if response.status_code == 200:
                    successes += 1
                    print(f"   ✓ Request {i+1}: Success")
                else:
                    failures += 1
                    print(f"   ✗ Request {i+1}: Failed (HTTP {response.status_code})")
            except httpx.HTTPStatusError as e:
                failures += 1
                print(f"   ✗ Request {i+1}: Failed (HTTP {e.response.status_code})")
        
        print(f"\n   Results: {successes} successes, {failures} failures")
        print()
        
        # 4. Get updated stats
        print("4. Updated Statistics")
        response = await client.get(f"{API_BASE_URL}/api/stats")
        stats = response.json()
        print(f"   Total Events: {stats['total_events']}")
        print(f"   Error Count: {stats['error_count']}")
        print(f"   Error Rate: {stats['error_rate_percent']:.2f}%")
        print(f"   Avg Latency: {stats['avg_latency_ms']:.2f} ms")
        print()
        
        # 5. Get recent telemetry
        print("5. Recent Telemetry (last 3 events)")
        response = await client.get(f"{API_BASE_URL}/api/telemetry?limit=3")
        telemetry = response.json()
        
        for event in telemetry['events']:
            timestamp = event['timestamp'][:19]
            event_type = event['event_type'].upper()
            endpoint = event['endpoint']
            status = event['status_code']
            latency = event['latency_ms']
            
            print(f"   [{timestamp}] {event_type:8} {endpoint:20} HTTP {status:3} ({latency:.0f}ms)")
            
            if event['error_message']:
                print(f"      Error: {event['error_message']}")
            
            if event['analysis']:
                analysis = event['analysis'][:100]
                print(f"      AI: {analysis}...")
        
        print()
        print("✓ Example completed!")
        print(f"\nView the dashboard at http://localhost:8501")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except httpx.ConnectError:
        print("\n❌ Error: Cannot connect to API server")
        print("   Make sure the API server is running:")
        print("   python api.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
