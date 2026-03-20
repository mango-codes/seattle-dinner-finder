#!/usr/bin/env python3
"""
Batch check availability for multiple restaurants using LLM parsing
"""

import json
import sys
from datetime import datetime
from check_availability import check_restaurant_availability, parse_availability_with_llm

# Try to import OpenClaw for LLM calls
try:
    # This would be replaced with actual OpenClaw API call
    HAS_OPENCLAW = False
except ImportError:
    HAS_OPENCLAW = False

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


def mock_llm_parse(prompt):
    """
    Mock LLM parsing - in production, this would call OpenClaw or another LLM
    For now, we'll do simple pattern matching
    """
    # Simple heuristic parsing
    content = prompt.lower()
    
    # Look for time patterns
    import re
    time_pattern = r'(\d{1,2}):(\d{2})\s*(am|pm)'
    matches = re.findall(time_pattern, content, re.IGNORECASE)
    
    times = []
    for hour, minute, period in matches:
        time_str = f"{hour}:{minute} {period.upper()}"
        # Filter to dinner hours (5:30 PM - 9:30 PM)
        if period.lower() == 'pm':
            h = int(hour)
            if 5 <= h <= 9:
                times.append(time_str)
    
    # Remove duplicates
    times = list(dict.fromkeys(times))
    
    if times:
        return {
            "available_times": times[:10],
            "has_dinner_availability": True,
            "notes": f"Found {len(times)} potential dinner times",
            "confidence": "medium"
        }
    else:
        return {
            "available_times": [],
            "has_dinner_availability": False,
            "notes": "No specific times found in page content. Restaurant may require direct booking or be fully booked.",
            "confidence": "low"
        }


def check_all_restaurants(date=None, party_size=2, output_file=None):
    """Check availability for all configured restaurants"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    results = []
    available_restaurants = []
    
    print(f"🔍 Checking availability for {len(RESTAURANTS)} restaurants on {date}...")
    print()
    
    for restaurant in RESTAURANTS:
        print(f"  Checking {restaurant['name']}...", end=" ", flush=True)
        
        # Fetch page content
        result = check_restaurant_availability(restaurant, date, party_size)
        
        if result.get('status') == 'success':
            # Parse with LLM (or mock)
            prompt = parse_availability_with_llm(result, date, party_size)
            parsed = mock_llm_parse(prompt)
            
            # Merge results
            full_result = {
                **restaurant,
                'date': date,
                'party_size': party_size,
                'url': result['url'],
                'available_times': parsed['available_times'],
                'has_dinner_availability': parsed['has_dinner_availability'],
                'notes': parsed['notes'],
                'confidence': parsed['confidence']
            }
            
            results.append(full_result)
            
            if parsed['has_dinner_availability']:
                print(f"✅ {len(parsed['available_times'])} dinner slots ({parsed['confidence']} confidence)")
                available_restaurants.append(full_result)
            else:
                print(f"⚠️ No dinner availability ({parsed['confidence']} confidence)")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
            results.append({
                **restaurant,
                'date': date,
                'error': result.get('error', 'Unknown error'),
                'status': 'error'
            })
    
    print()
    print(f"✅ Found {len(available_restaurants)} restaurants with dinner availability")
    
    output = {
        "date": date,
        "party_size": party_size,
        "total_checked": len(RESTAURANTS),
        "available_count": len(available_restaurants),
        "restaurants": results
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n💾 Results saved to {output_file}")
    
    return output


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch check restaurant availability with LLM parsing')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    result = check_all_restaurants(args.date, args.party_size, args.output)
    
    if not args.output:
        print("\n📊 Results:")
        print(json.dumps(result, indent=2))
