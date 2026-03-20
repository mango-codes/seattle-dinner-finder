from scrapling.fetchers import StealthyFetcher, DynamicFetcher
from scrapling.parser import Selector
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import time

class ReservationScraper:
    def __init__(self, headless=True):
        self.headless = headless
        
    def check_opentable(self, restaurant_slug, date, party_size=2, time_pref="19:00"):
        """
        Check availability on OpenTable
        
        Args:
            restaurant_slug: OpenTable URL slug (e.g., 'revel-seattle')
            date: YYYY-MM-DD format
            party_size: Number of people
            time_pref: Preferred time (HH:MM format)
        """
        url = f"https://www.opentable.com/r/{restaurant_slug}"
        
        try:
            # Use StealthyFetcher to bypass bot detection
            page = StealthyFetcher.fetch(
                url, 
                headless=self.headless,
                network_idle=True,
                wait_for='.reservation-time'  # Wait for time slots to load
            )
            
            # Look for time slot buttons
            time_buttons = page.css('button[data-testid*="time"]')
            
            available_times = []
            for btn in time_buttons:
                time_text = btn.css('::text').get()
                if time_text:
                    # Clean up time format
                    time_clean = time_text.strip()
                    available_times.append(time_clean)
            
            # Check if any times are in dinner window (6-9 PM)
            dinner_times = self._filter_dinner_times(available_times)
            
            return {
                "restaurant": restaurant_slug,
                "platform": "opentable",
                "date": date,
                "party_size": party_size,
                "url": url,
                "all_times": available_times[:10],  # Limit to first 10
                "dinner_window_times": dinner_times,
                "has_dinner_availability": len(dinner_times) > 0,
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
    
    def check_resy(self, venue_id, date, party_size=2):
        """
        Check availability on Resy
        
        Args:
            venue_id: Resy venue ID
            date: YYYY-MM-DD format
            party_size: Number of people
        """
        # Resy uses a different URL structure
        url = f"https://resy.com/cities/seattle-wa/venues/{venue_id}"
        
        try:
            page = DynamicFetcher.fetch(
                url,
                headless=self.headless,
                network_idle=True
            )
            
            # Resy loads times dynamically, look for time slot elements
            time_slots = page.css('[data-testid="time-slot"], .ReservationTimeSlot')
            
            available_times = []
            for slot in time_slots:
                time_text = slot.css('::text').get()
                if time_text:
                    available_times.append(time_text.strip())
            
            dinner_times = self._filter_dinner_times(available_times)
            
            return {
                "restaurant": venue_id,
                "platform": "resy",
                "date": date,
                "party_size": party_size,
                "url": url,
                "all_times": available_times[:10],
                "dinner_window_times": dinner_times,
                "has_dinner_availability": len(dinner_times) > 0,
                "status": "success"
            }
            
        except Exception as e:
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
        """
        Check availability on Tock
        
        Args:
            venue_slug: Tock venue slug (e.g., 'westward-seattle')
            date: YYYY-MM-DD format
            party_size: Number of people
        """
        url = f"https://www.exploretock.com/{venue_slug}/"
        
        try:
            page = DynamicFetcher.fetch(
                url,
                headless=self.headless,
                network_idle=True
            )
            
            # Tock uses different selectors
            time_buttons = page.css('button[data-testid*="time"], .time-slot')
            
            available_times = []
            for btn in time_buttons:
                time_text = btn.css('::text').get()
                if time_text:
                    available_times.append(time_text.strip())
            
            dinner_times = self._filter_dinner_times(available_times)
            
            return {
                "restaurant": venue_slug,
                "platform": "tock",
                "date": date,
                "party_size": party_size,
                "url": url,
                "all_times": available_times[:10],
                "dinner_window_times": dinner_times,
                "has_dinner_availability": len(dinner_times) > 0,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "restaurant": venue_slug,
                "platform": "tock",
                "date": date,
                "party_size": party_size,
                "url": url,
                "error": str(e),
                "status": "error"
            }
    
    def _filter_dinner_times(self, times):
        """Filter times to dinner window (6:00 PM - 9:30 PM)"""
        dinner_times = []
        
        for time_str in times:
            # Parse various time formats
            parsed = self._parse_time(time_str)
            if parsed:
                hour = parsed.hour
                # Dinner window: 6 PM to 9:30 PM
                if 18 <= hour < 21 or (hour == 21 and parsed.minute <= 30):
                    dinner_times.append(time_str)
        
        return dinner_times
    
    def _parse_time(self, time_str):
        """Parse time string to datetime object"""
        formats = [
            "%I:%M %p",
            "%I %p",
            "%H:%M",
        ]
        
        time_str = time_str.strip().upper()
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        return None


def check_restaurant_availability(restaurant_config, date, party_size=2):
    """
    Check availability for a single restaurant
    
    Args:
        restaurant_config: Dict with 'name', 'platform', 'slug', etc.
        date: YYYY-MM-DD
        party_size: Number of people
    """
    scraper = ReservationScraper(headless=True)
    
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
    
    parser = argparse.ArgumentParser(description='Check restaurant availability')
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
    print(json.dumps(result, indent=2))
