#!/usr/bin/env python3
"""
Convert scraper output to the format expected by the website builder
"""

import json
import sys
from datetime import datetime

def convert_to_site_format(scraper_data):
    """Convert scraper JSON to website format"""
    
    restaurants = []
    
    for r in scraper_data.get('restaurants', []):
        # Skip restaurants with errors
        if r.get('status') == 'error':
            continue
        
        # Format available times for display
        available_times = r.get('available_times', [])
        has_availability = len(available_times) > 0
        
        # Create display format
        restaurant = {
            "name": r['name'],
            "neighborhood": r['neighborhood'],
            "cuisine": r['cuisine'],
            "price": r['price'],
            "vibes": ["🍽️ Dinner"] if has_availability else ["📞 Call for availability"],
            "address": "See reservation link",
            "phone": "See reservation link",
            "reservationUrl": r['url'],
            "availability": "available" if has_availability else "limited",
            "whyFun": f"Available times: {', '.join(available_times[:5])}" if has_availability else r.get('notes', 'Check reservation site for availability'),
            "available_times": available_times,
            "confidence": r.get('confidence', 'low')
        }
        
        restaurants.append(restaurant)
    
    return restaurants

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert scraper data to site format')
    parser.add_argument('--input', required=True, help='Input JSON file from scraper')
    parser.add_argument('--output', required=True, help='Output JSON file for site')
    
    args = parser.parse_args()
    
    # Load scraper data
    with open(args.input, 'r') as f:
        scraper_data = json.load(f)
    
    # Convert
    site_data = convert_to_site_format(scraper_data)
    
    # Save
    with open(args.output, 'w') as f:
        json.dump(site_data, f, indent=2)
    
    print(f"✅ Converted {len(site_data)} restaurants to site format")
