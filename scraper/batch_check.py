#!/usr/bin/env python3
"""
Daily restaurant discovery - focuses on finding great restaurants
Availability must be checked directly on reservation sites
"""

import json
import sys
from datetime import datetime
from discover import discover_restaurant

# Restaurant database - curated list of fun restaurants
RESTAURANTS = [
    {
        "name": "Revel",
        "slug": "revel-seattle",
        "platform": "opentable",
        "neighborhood": "Fremont",
        "cuisine": "Korean Fusion",
        "price": "$$",
        "vibes": ["🔥 Open Kitchen", "🍜 Shareable Plates", "🎉 Lively"],
        "whyFun": "Chef Rachel Yang's creative Korean comfort food with a massive open kitchen. Perfect for sharing and the energy is always buzzing."
    },
    {
        "name": "The Ballard Cut",
        "slug": "the-ballard-cut-seattle",
        "platform": "opentable",
        "neighborhood": "Ballard",
        "cuisine": "Steakhouse",
        "price": "$$$",
        "vibes": ["🥃 Whiskey Bar", "🥩 Steakhouse", "✨ Upscale Casual"],
        "whyFun": "Farm-to-table steakhouse with an incredible Japanese whiskey selection. Upscale but approachable, great for a celebratory night."
    },
    {
        "name": "Grappa",
        "slug": "grappa-seattle",
        "platform": "opentable",
        "neighborhood": "Queen Anne",
        "cuisine": "Italian",
        "price": "$$",
        "vibes": ["🍝 Handmade Pasta", "🍷 Wine Bar", "💕 Romantic"],
        "whyFun": "Upper Queen Anne's hidden gem with fresh handmade pasta and an extensive grappa and wine list. Intimate and perfect for date night."
    },
    {
        "name": "RockCreek Seafood & Spirits",
        "slug": "rockcreek-seafood-and-spirits-seattle",
        "platform": "opentable",
        "neighborhood": "Fremont",
        "cuisine": "Seafood",
        "price": "$$",
        "vibes": ["🦐 Fresh Seafood", "🌿 Global Flavors", "🔥 Wood-Fired"],
        "whyFun": "James Beard semifinalist Chef Eric Donnelly's flagship. Globally sourced seafood with bold flavors in a rustic-industrial space."
    },
    {
        "name": "Westward",
        "slug": "westward-seattle",
        "platform": "tock",
        "neighborhood": "Green Lake",
        "cuisine": "Seafood",
        "price": "$$",
        "vibes": ["🌅 Lake Views", "🦪 Oysters", "🏖️ Beach Vibes"],
        "whyFun": "Located in a colorful converted gas station on Green Lake with a deck patio for sunset views. Like dining at a Pacific Northwest beach house."
    },
    {
        "name": "Joule",
        "slug": "joule",
        "platform": "opentable",
        "neighborhood": "Fremont",
        "cuisine": "Korean Steakhouse",
        "price": "$$",
        "vibes": ["🥩 Korean Steakhouse", "✨ Creative", "🍷 Full Bar"],
        "whyFun": "From celebrated chefs Rachel Yang & Seif Chirchi. Modern Korean steakhouse with nontraditional cuts in the stylish Fremont Collective."
    },
    {
        "name": "Toulouse Petit",
        "slug": "toulouse-petit-kitchen-and-lounge",
        "platform": "opentable",
        "neighborhood": "Queen Anne",
        "cuisine": "Creole",
        "price": "$$",
        "vibes": ["🎷 New Orleans", "🍤 Creole", "🕯️ Candlelit"],
        "whyFun": "New Orleans-style with ornate French Quarter decor, candlelit ambiance, and fantastic Shrimp & Grits. Very popular—book early!"
    },
    {
        "name": "How to Cook a Wolf",
        "slug": "how-to-cook-a-wolf",
        "platform": "opentable",
        "neighborhood": "Queen Anne",
        "cuisine": "Italian",
        "price": "$$$",
        "vibes": ["🍝 Handmade Pasta", "🔥 Cozy", "✨ Ethan Stowell"],
        "whyFun": "Ethan Stowell's Italian-inspired spot. Cozy, intimate, handmade pasta with local ingredients. Perfect for date night."
    }
]


def discover_all_restaurants(date=None, party_size=2):
    """Generate daily restaurant recommendations"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    results = []
    
    print(f"🔍 Discovering restaurants for {date}...")
    print()
    
    for restaurant in RESTAURANTS:
        print(f"  ✓ {restaurant['name']} ({restaurant['neighborhood']})", flush=True)
        
        # Build the result
        result = {
            **restaurant,
            'date': date,
            'party_size': party_size,
            'reservationUrl': get_reservation_url(restaurant),
            'availability': 'check_directly',
            'checkAvailabilityNote': 'Click to check live availability'
        }
        
        results.append(result)
    
    print()
    print(f"✅ Found {len(results)} great restaurants")
    
    return {
        "date": date,
        "party_size": party_size,
        "total_restaurants": len(results),
        "restaurants": results,
        "note": "Availability changes frequently. Click reservation links to check live availability."
    }


def get_reservation_url(restaurant):
    """Generate the reservation URL for a restaurant"""
    platform = restaurant.get('platform', 'opentable')
    slug = restaurant.get('slug')
    
    if platform == 'opentable':
        return f"https://www.opentable.com/r/{slug}"
    elif platform == 'resy':
        return f"https://resy.com/cities/seattle-wa/venues/{slug}"
    elif platform == 'tock':
        return f"https://www.exploretock.com/{slug}/"
    else:
        return "#"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily restaurant discovery')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    result = discover_all_restaurants(args.date, args.party_size)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")
    else:
        print("\n📊 Results:")
        print(json.dumps(result, indent=2))
