#!/usr/bin/env python3
"""
generate_schedule.py
--------------------
Fetches ICS calendar feed(s) listed in config.json and writes
schedule.json for the availability page to display.

Usage:
    python generate_schedule.py

Requirements:
    pip install icalendar requests pytz
"""

import json
import os
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

try:
    import requests
    from icalendar import Calendar
    import pytz
except ImportError:
    print(
        "Missing dependencies. Please run:\n"
        "  pip install icalendar requests pytz",
        file=sys.stderr,
    )
    sys.exit(1)


ROOT = Path(__file__).parent


def get_fetch_range(tz):
    """Return (start, end) covering the current week plus the next 4 weeks."""
    today = date.today()
    # Start from the Monday of the current week
    monday = today - timedelta(days=today.weekday())
    range_start = tz.localize(datetime(monday.year, monday.month, monday.day, 0, 0, 0))
    range_end = range_start + timedelta(weeks=5)
    return range_start, range_end


def parse_ics_url(url, range_start, range_end, local_tz):
    """
    Fetch one ICS URL and return a list of event dicts within the given range.
    Event titles are anonymised to 'Busy' for privacy.
    """
    events = []
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.content)
    except Exception as exc:
        print(f"  ⚠️  Could not fetch {url[:70]}: {exc}", file=sys.stderr)
        return events

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        dtstart = component.get("DTSTART")
        dtend = component.get("DTEND") or component.get("DTSTART")
        if not dtstart:
            continue

        # Skip events marked as "free" (transparent) - standard ICS
        transp = component.get("TRANSP")
        if transp and str(transp).upper() == "TRANSPARENT":
            continue

        # Skip events marked as "free" in Outlook/Microsoft calendars
        busystatus = component.get("X-MICROSOFT-CDO-BUSYSTATUS")
        if busystatus and str(busystatus).upper() == "FREE":
            continue

        raw_start = dtstart.dt
        raw_end = dtend.dt if dtend else raw_start

        # Normalise to aware datetime
        if isinstance(raw_start, date) and not isinstance(raw_start, datetime):
            # All-day event — treat as full day in local timezone
            start = local_tz.localize(
                datetime(raw_start.year, raw_start.month, raw_start.day, 0, 0, 0)
            )
            end = local_tz.localize(
                datetime(raw_end.year, raw_end.month, raw_end.day, 0, 0, 0)
            )
        else:
            start = raw_start if raw_start.tzinfo else local_tz.localize(raw_start)
            end = raw_end if raw_end.tzinfo else local_tz.localize(raw_end)
            start = start.astimezone(local_tz)
            end = end.astimezone(local_tz)

        # Skip events outside the fetch range
        if start >= range_end or end <= range_start:
            continue

        events.append(
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
                # Anonymise: only show that time is busy, not what for
                "summary": "Busy",
            }
        )

    return events


def main():
    config_path = ROOT / "config.json"
    if not config_path.exists():
        print("config.json not found.", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    tz_name = config.get("timezone", "UTC")
    try:
        local_tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        print(f"Unknown timezone '{tz_name}'. Using UTC.", file=sys.stderr)
        local_tz = pytz.UTC

    # Prefer the ICS_URLS environment variable (set via GitHub Secrets)
    # so URLs are never stored in the repo. Fall back to config.json for
    # local testing.
    env_urls = os.environ.get("ICS_URLS", "")
    if env_urls.strip():
        ics_urls = [u.strip() for u in env_urls.split(",") if u.strip()]
    else:
        ics_urls = [
            u for u in config.get("icsUrls", []) if u and u != "YOUR_ICS_URL_HERE"
        ]
    configured = len(ics_urls) > 0

    range_start, range_end = get_fetch_range(local_tz)
    all_events = []

    for url in ics_urls:
        print(f"Fetching: {url[:70]}…")
        evts = parse_ics_url(url, range_start, range_end, local_tz)
        all_events.extend(evts)
        print(f"  → {len(evts)} event(s) found")

    output = {
        "lastUpdated": datetime.now(local_tz).isoformat(),
        "timezone": tz_name,
        "ownerName": config.get("ownerName", "Nikki"),
        "weeklyProjectHours": config.get("weeklyProjectHours", 20),
        "workdayStart": config.get("workdayStart", 8),
        "workdayEnd": config.get("workdayEnd", 19),
        "configured": configured,
        "events": all_events,
    }

    out_path = ROOT / "schedule.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ schedule.json written ({len(all_events)} total event(s))")


if __name__ == "__main__":
    main()
