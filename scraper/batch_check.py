#!/usr/bin/env python3
"""
Batch check availability for multiple restaurants
"""

import json
import sys
from datetime import datetime
from check_availability import check_restaurant_availability

# Restaurant configurations
RESTAURANTS = [
    {
        "name": "Revel",
        "slug": "revel-seattle",
        "platform": "opentable",
        "neighborhood": "Fremont",
        "cuisine": "Korean Fusion",
        "price": "$$"
    },
    {
        "name": "The Ballard Cut",
        "slug": "the-ballard-cut-seattle",
        "platform": "opentable",
        "neighborhood": "Ballard",
        "cuisine": "Steakhouse",
        "price": "$$$"
    },
    {
        "name": "Grappa",
        "slug": "grappa-seattle",
        "platform": "opentable",
        "neighborhood": "Queen Anne",
        "cuisine": "Italian",
        "price": "$$"
    },
    {
        "name": "RockCreek Seafood & Spirits",
        "slug": "rockcreek-seafood-and-spirits-seattle",
        "platform": "opentable",
        "neighborhood": "Fremont",
        "cuisine": "Seafood",
        "price": "$$"
    },
    {
        "name": "Westward",
        "slug": "westward-seattle",
        "platform": "tock",
        "neighborhood": "Green Lake",
        "cuisine": "Seafood",
        "price": "$$"
    },
    {
        "name": "Joule",
        "slug": "joule",
        "platform": "opentable",
        "neighborhood": "Fremont",
        "cuisine": "Korean Steakhouse",
        "price": "$$"
    }
]


def check_all_restaurants(date=None, party_size=2):
    """Check availability for all configured restaurants"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    results = []
    available_restaurants = []
    
    print(f"🔍 Checking availability for {len(RESTAURANTS)} restaurants on {date}...")
    print()
    
    for restaurant in RESTAURANTS:
        print(f"  Checking {restaurant['name']}...", end=" ")
        
        result = check_restaurant_availability(restaurant, date, party_size)
        results.append(result)
        
        if result.get('status') == 'success':
            if result.get('has_dinner_availability'):
                print(f"✅ {len(result['dinner_window_times'])} dinner slots")
                available_restaurants.append({
                    **restaurant,
                    'available_times': result['dinner_window_times'],
                    'all_times': result['all_times']
                })
            else:
                print(f"⚠️ No dinner availability")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
    
    print()
    print(f"✅ Found {len(available_restaurants)} restaurants with dinner availability")
    
    return {
        "date": date,
        "party_size": party_size,
        "total_checked": len(RESTAURANTS),
        "available_count": len(available_restaurants),
        "available_restaurants": available_restaurants,
        "all_results": results
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch check restaurant availability')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    result = check_all_restaurants(args.date, args.party_size)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")
    else:
        print("\n📊 Results:")
        print(json.dumps(result, indent=2))
