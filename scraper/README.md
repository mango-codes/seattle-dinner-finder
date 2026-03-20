# Reservation Availability Scraper

Uses Scrapling to check real-time reservation availability on OpenTable, Resy, and Tock.

## Installation

```bash
pip install scrapling
scrapling install  # Install browser dependencies
```

## Usage

```bash
python scraper/check_availability.py --restaurant revel --platform opentable --date 2026-03-21 --party-size 2
```

## Supported Platforms

- **OpenTable** - Most restaurants
- **Resy** - Higher-end spots
- **Tock** - Fine dining, experiences

## Output

Returns JSON with available time slots:
```json
{
  "restaurant": "Revel",
  "platform": "opentable",
  "date": "2026-03-21",
  "party_size": 2,
  "available_times": ["6:00 PM", "7:30 PM", "9:00 PM"],
  "target_window_available": true
}
```
