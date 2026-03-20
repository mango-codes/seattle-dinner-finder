#!/usr/bin/env python3
"""
Browser automation using Playwright directly with stealth
"""

import json
import re
from playwright.sync_api import sync_playwright
try:
    from playwright_stealth import stealth_sync
except ImportError:
    # Fallback if stealth_sync not available
    def stealth_sync(page):
        pass

def fetch_with_stealth(url, wait_for=None, timeout=30000):
    """
    Fetch page using Playwright with stealth mode
    """
    with sync_playwright() as p:
        # Launch browser with stealth
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Apply stealth
        stealth_sync(page)
        
        try:
            # Navigate to page
            page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Wait for specific selector if provided
            if wait_for:
                page.wait_for_selector(wait_for, timeout=timeout)
            
            # Get page content
            content = page.content()
            
            browser.close()
            return content
            
        except Exception as e:
            browser.close()
            raise e


def check_opentable_availability(restaurant_slug, date, party_size=2):
    """
    Check OpenTable availability using Playwright
    """
    url = f"https://www.opentable.com/r/{restaurant_slug}"
    
    try:
        print(f"    [Stealth browser] Fetching {url}...", flush=True)
        html = fetch_with_stealth(url, wait_for='body', timeout=45000)
        
        # Extract text
        text = extract_text(html)
        
        return {
            "restaurant": restaurant_slug,
            "platform": "opentable",
            "date": date,
            "party_size": party_size,
            "url": url,
            "page_content": text[:15000],
            "html_length": len(html),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "restaurant": restaurant_slug,
            "platform": "opentable",
            "date": date,
            "party_size": party_size,
            "url": url,
            "error": str(e),
            "status": "error"
        }


def extract_text(html):
    """Extract readable text from HTML"""
    import re
    
    # Remove script and style
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check availability with stealth browser')
    parser.add_argument('--restaurant', required=True, help='Restaurant slug')
    parser.add_argument('--date', required=True, help='Date YYYY-MM-DD')
    parser.add_argument('--party-size', type=int, default=2)
    
    args = parser.parse_args()
    
    result = check_opentable_availability(args.restaurant, args.date, args.party_size)
    print(json.dumps(result, indent=2))
