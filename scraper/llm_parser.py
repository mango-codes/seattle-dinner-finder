#!/usr/bin/env python3
"""
LLM-powered availability parser
Uses OpenClaw or direct API to extract reservation times from page content
"""

import json
import os
import subprocess
import re

def parse_with_openclaw(page_content, restaurant_name, date, party_size):
    """
    Use OpenClaw to parse availability from page content
    """
    prompt = f"""You are analyzing a restaurant reservation page to find available dinner times.

Restaurant: {restaurant_name}
Date: {date}
Party Size: {party_size}

Here is the text content from the reservation page:

---
{page_content[:8000]}
---

Your task:
1. Look for available reservation times for {party_size} people on {date}
2. Focus on DINNER times (between 5:30 PM and 9:30 PM)
3. Extract ALL available times you find - be thorough
4. Look for patterns like "5:30 PM", "6:00", "7:30", etc.
5. If you see time slots mentioned, list them all

Respond ONLY in this exact JSON format:
{{
  "available_times": ["6:00 PM", "7:30 PM", "9:00 PM"],
  "has_dinner_availability": true,
  "notes": "Brief description of what you found",
  "confidence": "high"
}}

If you cannot find specific times, return:
{{
  "available_times": [],
  "has_dinner_availability": false,
  "notes": "No specific times found - restaurant may be booked or require direct call",
  "confidence": "low"
}}

IMPORTANT: Return ONLY the JSON, no other text."""

    try:
        # Try to use OpenClaw if available
        result = subprocess.run(
            ['openclaw', 'ask', '--message', prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse the response
            response_text = result.stdout.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        
        # Fallback to mock parsing if OpenClaw fails
        return parse_with_regex(page_content)
        
    except Exception as e:
        print(f"OpenClaw parsing failed: {e}")
        return parse_with_regex(page_content)


def parse_with_regex(page_content):
    """
    Fallback regex-based parsing
    """
    import re
    
    # Look for time patterns
    time_pattern = r'(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)'
    matches = re.findall(time_pattern, page_content)
    
    times = []
    for hour, minute, period in matches:
        time_str = f"{hour}:{minute} {period.upper()}"
        # Filter to dinner hours (5:30 PM - 9:30 PM)
        if period.lower() == 'pm':
            h = int(hour)
            m = int(minute)
            if (h == 5 and m >= 30) or (6 <= h <= 9):
                times.append(time_str)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_times = []
    for t in times:
        if t not in seen:
            seen.add(t)
            unique_times.append(t)
    
    if unique_times:
        return {
            "available_times": unique_times[:10],
            "has_dinner_availability": True,
            "notes": f"Found {len(unique_times)} potential dinner times via pattern matching",
            "confidence": "medium"
        }
    else:
        return {
            "available_times": [],
            "has_dinner_availability": False,
            "notes": "No specific times found in page content",
            "confidence": "low"
        }


def parse_availability(page_content, restaurant_name, date, party_size=2):
    """
    Main entry point for parsing availability
    Tries OpenClaw first, falls back to regex
    """
    # Try OpenClaw first
    result = parse_with_openclaw(page_content, restaurant_name, date, party_size)
    
    # Validate result
    if isinstance(result, dict) and 'available_times' in result:
        return result
    
    # Fallback
    return parse_with_regex(page_content)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse availability with LLM')
    parser.add_argument('--content', required=True, help='Page content to parse')
    parser.add_argument('--restaurant', required=True, help='Restaurant name')
    parser.add_argument('--date', required=True, help='Date')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    
    args = parser.parse_args()
    
    result = parse_availability(args.content, args.restaurant, args.date, args.party_size)
    print(json.dumps(result, indent=2))
