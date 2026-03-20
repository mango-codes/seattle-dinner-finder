from scrapling.fetchers import Fetcher
import json
import re
from datetime import datetime

class RestaurantDiscoveryScraper:
    """
    Focus on discovering restaurants, not scraping availability
    Reservation sites block bots, so we provide links for users to check directly
    """
    
    def __init__(self):
        self.fetcher = Fetcher()
        
    def discover_opentable(self, restaurant_slug):
        """Get restaurant info from OpenTable page"""
        url = f"https://www.opentable.com/r/{restaurant_slug}"
        
        try:
            page = self.fetcher.get(url, stealthy_headers=True)
            html = page.text
            
            # Extract basic info from meta tags and page content
            name = self._extract_name(html) or restaurant_slug.replace('-', ' ').title()
            
            return {
                "name": name,
                "slug": restaurant_slug,
                "platform": "opentable",
                "url": url,
                "status": "active",
                "error": None
            }
            
        except Exception as e:
            return {
                "name": restaurant_slug.replace('-', ' ').title(),
                "slug": restaurant_slug,
                "platform": "opentable",
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    def discover_resy(self, venue_id):
        """Get restaurant info from Resy"""
        url = f"https://resy.com/cities/seattle-wa/venues/{venue_id}"
        
        try:
            page = self.fetcher.get(url, stealthy_headers=True)
            
            return {
                "name": venue_id.replace('-', ' ').title(),
                "slug": venue_id,
                "platform": "resy",
                "url": url,
                "status": "active",
                "error": None
            }
            
        except Exception as e:
            return {
                "name": venue_id.replace('-', ' ').title(),
                "slug": venue_id,
                "platform": "resy",
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    def discover_tock(self, venue_slug):
        """Get restaurant info from Tock"""
        url = f"https://www.exploretock.com/{venue_slug}/"
        
        try:
            page = self.fetcher.get(url, stealthy_headers=True)
            
            return {
                "name": venue_slug.replace('-', ' ').title(),
                "slug": venue_slug,
                "platform": "tock",
                "url": url,
                "status": "active",
                "error": None
            }
            
        except Exception as e:
            return {
                "name": venue_slug.replace('-', ' ').title(),
                "slug": venue_slug,
                "platform": "tock",
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    def _extract_name(self, html):
        """Try to extract restaurant name from HTML"""
        # Look for title tag or meta tags
        import re
        
        # Try title tag
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            # Clean up title (often "Restaurant Name - OpenTable")
            return title.split(' - ')[0].split(' | ')[0].strip()
        
        return None


def discover_restaurant(restaurant_config):
    """Discover a single restaurant"""
    scraper = RestaurantDiscoveryScraper()
    
    platform = restaurant_config.get('platform', 'opentable')
    slug = restaurant_config.get('slug')
    
    if not slug:
        return {
            "error": "No slug provided",
            "status": "error"
        }
    
    if platform == 'opentable':
        return scraper.discover_opentable(slug)
    elif platform == 'resy':
        return scraper.discover_resy(slug)
    elif platform == 'tock':
        return scraper.discover_tock(slug)
    else:
        return {
            "error": f"Unsupported platform: {platform}",
            "status": "error"
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Discover restaurant info')
    parser.add_argument('--restaurant', required=True, help='Restaurant slug')
    parser.add_argument('--platform', default='opentable', choices=['opentable', 'resy', 'tock'])
    
    args = parser.parse_args()
    
    config = {
        'slug': args.restaurant,
        'platform': args.platform
    }
    
    result = discover_restaurant(config)
    print(json.dumps(result, indent=2))
