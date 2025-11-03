#!/usr/bin/env python3
"""
Nightly Report Generator
Generates daily CSV reports and summary statistics.
Run this via cron/scheduler at midnight daily.

NOTE: This script accesses the backend's ledger via API endpoint
to ensure it sees the same data as the running backend server.
If the backend is not running, it will fall back to local ledger.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import requests

# Add billing directory to path
billing_dir = Path(__file__).parent
sys.path.insert(0, str(billing_dir.parent))

from billing.ledger import get_ledger


def generate_report(yesterday: bool = True, use_api: bool = True):
    """
    Generate CSV report for previous day (or today if yesterday=False).
    
    Args:
        yesterday: If True, generate for yesterday (default). If False, generate for today.
        use_api: If True, use API endpoint (recommended). If False, use local ledger.
    """
    if yesterday:
        target_date = date.today() - timedelta(days=1)
    else:
        target_date = date.today()
    
    target_date_str = target_date.isoformat()
    
    # Try to use API endpoint first (to access backend's ledger data)
    if use_api:
        try:
            api_url = "http://localhost:8011"
            
            # Get CSV report from API
            csv_url = f"{api_url}/api/billing/report/csv/{target_date_str}"
            response = requests.get(csv_url, timeout=5)
            
            if response.status_code == 200:
                # Save CSV file
                csv_path = billing_dir / "reports" / f"billing_report_{target_date_str}.csv"
                csv_path.parent.mkdir(parents=True, exist_ok=True)
                csv_path.write_bytes(response.content)
                
                # Get statistics from API
                stats_url = f"{api_url}/api/billing/daily?target_date={target_date_str}"
                stats_response = requests.get(stats_url, timeout=5)
                
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                else:
                    # Fallback to local ledger for stats
                    ledger = get_ledger()
                    stats = ledger.get_daily_stats(target_date)
            else:
                raise requests.RequestException(f"API returned {response.status_code}")
                
        except (requests.RequestException, requests.ConnectionError) as e:
            print(f"⚠️  Warning: Could not connect to backend API ({e})")
            print(f"   Falling back to local ledger (may not have backend's data)\n")
            use_api = False
    
    # Fallback to local ledger
    if not use_api:
        ledger = get_ledger()
        csv_path = ledger.generate_daily_csv(target_date)
        stats = ledger.get_daily_stats(target_date)
    
    print(f"Generated report for {target_date_str}")
    print(f"CSV file: {csv_path}")
    print(f"\nDaily Statistics:")
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Total cost: ${stats['total_cost_usd']:.4f}")
    print(f"  Input tokens: {stats['total_input_tokens']:,}")
    print(f"  Output tokens: {stats['total_output_tokens']:,}")
    print(f"  Full mode: {stats['full_mode_turns']}")
    print(f"  Lite mode: {stats['lite_mode_turns']}")
    print(f"  Over budget turns: {stats['over_budget_turns']}")
    print(f"  Budget limit: ${stats['budget_limit_usd']:.2f}")
    print(f"  Budget remaining: ${stats['budget_remaining_usd']:.4f}")
    
    return csv_path, stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate nightly billing report")
    parser.add_argument(
        "--today",
        action="store_true",
        help="Generate report for today instead of yesterday"
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Don't use API endpoint (use local ledger only)"
    )
    
    args = parser.parse_args()
    
    try:
        csv_path, stats = generate_report(
            yesterday=not args.today,
            use_api=not args.no_api
        )
        sys.exit(0)
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)

