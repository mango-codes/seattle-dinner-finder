from scrapling.fetchers import StealthyFetcher
from scrapling.parser import Selector
import json
import re
from datetime import datetime

class ReservationScraper:
    def __init__(self):
        self.fetcher = StealthyFetcher()
        
    def check_opentable(self, restaurant_slug, date, party_size=2):
        """Check availability on OpenTable using Scrapling StealthyFetcher"""
        url = f"https://www.opentable.com/r/{restaurant_slug}"
        
        try:
            print(f"    [Scrapling Stealth] Fetching...", end=" ", flush=True)
            
            # Use StealthyFetcher with all protections enabled
            page = self.fetcher.fetch(
                url,
                headless=True,
                network_idle=True,
                google_search=False,  # Don't use Google as referer for OpenTable
                solve_cloudflare=True
            )
            
            print(f"✓", flush=True)
            
            # Get content
            html_content = page.text
            text_content = self._extract_text_content(html_content)
            
            return {
                "restaurant": restaurant_slug,
                "platform": "opentable",
                "date": date,
                "party_size": party_size,
                "url": url,
                "page_content": text_content[:15000],
                "html_length": len(html_content),
                "status": "success"
            }
            
        except Exception as e:
            print(f"✗ ({str(e)[:60]}...)", flush=True)
            return {
                "restaurant": restaurant_slug,
                "platform": "opentable",
                "date": date,
                "party_size": party_size,
                "url": url,
                "error": str(e),
                "status": "error"
            }
    
    def check_resy(self, venue_id, date, party_size=2):
        """Check availability on Resy"""
        url = f"https://resy.com/cities/seattle-wa/venues/{venue_id}"
        
        try:
            print(f"    [Scrapling Stealth] Fetching...", end=" ", flush=True)
            
            page = self.fetcher.fetch(
                url,
                headless=True,
                network_idle=True,
                solve_cloudflare=True
            )
            
            print(f"✓", flush=True)
            
            html_content = page.text
            text_content = self._extract_text_content(html_content)
            
            return {
                "restaurant": venue_id,
                "platform": "resy",
                "date": date,
                "party_size": party_size,
                "url": url,
                "page_content": text_content[:15000],
                "html_length": len(html_content),
                "status": "success"
            }
            
        except Exception as e:
            print(f"✗ ({str(e)[:60]}...)", flush=True)
            return {
                "restaurant": venue_id,
                "platform": "resy",
                "date": date,
                "party_size": party_size,
                "url": url,
                "error": str(e),
                "status": "error"
            }
    
    def check_tock(self, venue_slug, date, party_size=2):
        """Check availability on Tock"""
        url = f"https://www.exploretock.com/{venue_slug}/"
        
        try:
            print(f"    [Scrapling Stealth] Fetching...", end=" ", flush=True)
            
            page = self.fetcher.fetch(
                url,
                headless=True,
                network_idle=True,
                solve_cloudflare=True
            )
            
            print(f"✓", flush=True)
            
            html_content = page.text
            text_content = self._extract_text_content(html_content)
            
            return {
                "restaurant": venue_slug,
                "platform": "tock",
                "date": date,
                "party_size": party_size,
                "url": url,
                "page_content": text_content[:15000],
                "html_length": len(html_content),
                "status": "success"
            }
            
        except Exception as e:
            print(f"✗ ({str(e)[:60]}...)", flush=True)
            return {
                "restaurant": venue_slug,
                "platform": "tock",
                "date": date,
                "party_size": party_size,
                "url": url,
                "error": str(e),
                "status": "error"
            }
    
    def _extract_text_content(self, html):
        """Extract readable text from HTML"""
        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text


def check_restaurant_availability(restaurant_config, date, party_size=2):
    """Check availability for a single restaurant"""
    scraper = ReservationScraper()
    
    platform = restaurant_config.get('platform', 'opentable')
    slug = restaurant_config.get('slug')
    
    if not slug:
        return {
            "error": "No slug provided for restaurant",
            "status": "error"
        }
    
    if platform == 'opentable':
        return scraper.check_opentable(slug, date, party_size)
    elif platform == 'resy':
        return scraper.check_resy(slug, date, party_size)
    elif platform == 'tock':
        return scraper.check_tock(slug, date, party_size)
    else:
        return {
            "error": f"Unsupported platform: {platform}",
            "status": "error"
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check restaurant availability with Scrapling Stealth')
    parser.add_argument('--restaurant', required=True, help='Restaurant slug')
    parser.add_argument('--platform', default='opentable', choices=['opentable', 'resy', 'tock'])
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    
    args = parser.parse_args()
    
    config = {
        'slug': args.restaurant,
        'platform': args.platform
    }
    
    result = check_restaurant_availability(config, args.date, args.party_size)
    print("\n" + json.dumps(result, indent=2))
