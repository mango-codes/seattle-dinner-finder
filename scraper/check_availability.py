from scrapling.fetchers import Fetcher
from scrapling.parser import Selector
import json
import re
from datetime import datetime
import os

class ReservationScraper:
    def __init__(self):
        self.fetcher = Fetcher()
        
    def check_opentable(self, restaurant_slug, date, party_size=2):
        """Check availability on OpenTable and return page content for LLM parsing"""
        url = f"https://www.opentable.com/r/{restaurant_slug}"
        
        try:
            # Fetch the page
            page = self.fetcher.get(url, stealthy_headers=True)
            
            # Get the full HTML content
            html_content = page.text
            
            # Extract text content (remove scripts, styles, etc.)
            text_content = self._extract_text_content(html_content)
            
            # Look for reservation-related sections
            reservation_section = self._find_reservation_section(text_content)
            
            return {
                "restaurant": restaurant_slug,
                "platform": "opentable",
                "date": date,
                "party_size": party_size,
                "url": url,
                "page_content": reservation_section[:5000],  # Limit content length
                "full_text": text_content[:10000],
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
        """Check availability on Resy"""
        url = f"https://resy.com/cities/seattle-wa/venues/{venue_id}"
        
        try:
            page = self.fetcher.get(url, stealthy_headers=True)
            html_content = page.text
            text_content = self._extract_text_content(html_content)
            reservation_section = self._find_reservation_section(text_content)
            
            return {
                "restaurant": venue_id,
                "platform": "resy",
                "date": date,
                "party_size": party_size,
                "url": url,
                "page_content": reservation_section[:5000],
                "full_text": text_content[:10000],
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
        """Check availability on Tock"""
        url = f"https://www.exploretock.com/{venue_slug}/"
        
        try:
            page = self.fetcher.get(url, stealthy_headers=True)
            html_content = page.text
            text_content = self._extract_text_content(html_content)
            reservation_section = self._find_reservation_section(text_content)
            
            return {
                "restaurant": venue_slug,
                "platform": "tock",
                "date": date,
                "party_size": party_size,
                "url": url,
                "page_content": reservation_section[:5000],
                "full_text": text_content[:10000],
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
    
    def _extract_text_content(self, html):
        """Extract readable text from HTML"""
        # Remove script and style elements
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _find_reservation_section(self, text):
        """Find the section of text related to reservations/times"""
        # Look for keywords related to reservations
        keywords = [
            'reservation', 'book', 'table', 'time', 'available', 
            'party size', 'guests', 'dinner', 'lunch', 'breakfast',
            'PM', 'AM', ':00', ':30'
        ]
        
        lines = text.split('\n')
        relevant_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:  # Reasonable length
                if any(keyword.lower() in line.lower() for keyword in keywords):
                    relevant_lines.append(line)
        
        return '\n'.join(relevant_lines[:100])  # Limit to 100 lines


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


def parse_availability_with_llm(page_data, target_date, party_size=2):
    """
    Format page data for LLM parsing
    Returns a prompt that can be sent to an LLM to extract availability
    """
    prompt = f"""You are analyzing a restaurant reservation page to find available dinner times.

Restaurant: {page_data['restaurant']}
Platform: {page_data['platform']}
Date: {target_date}
Party Size: {party_size}
URL: {page_data['url']}

Here is the text content from the reservation page:

---
{page_data['page_content']}
---

Your task:
1. Look for available reservation times for {party_size} people on {target_date}
2. Focus on DINNER times (between 5:30 PM and 9:30 PM)
3. Extract all available times you find
4. If no specific times are shown, note what the page says about availability

Respond in this exact JSON format:
{{
  "available_times": ["6:00 PM", "7:30 PM", "9:00 PM"],
  "has_dinner_availability": true,
  "notes": "Any additional info about availability",
  "confidence": "high|medium|low"
}}

If you cannot find specific times, return:
{{
  "available_times": [],
  "has_dinner_availability": false,
  "notes": "Explanation of what you found (e.g., 'No times shown for this date', 'Restaurant appears fully booked', etc.)",
  "confidence": "low"
}}
"""
    
    return prompt


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check restaurant availability')
    parser.add_argument('--restaurant', required=True, help='Restaurant slug')
    parser.add_argument('--platform', default='opentable', choices=['opentable', 'resy', 'tock'])
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    parser.add_argument('--llm-prompt', action='store_true', help='Output LLM prompt instead of raw data')
    
    args = parser.parse_args()
    
    config = {
        'slug': args.restaurant,
        'platform': args.platform
    }
    
    result = check_restaurant_availability(config, args.date, args.party_size)
    
    if args.llm_prompt and result.get('status') == 'success':
        prompt = parse_availability_with_llm(result, args.date, args.party_size)
        print(prompt)
    else:
        print(json.dumps(result, indent=2))
