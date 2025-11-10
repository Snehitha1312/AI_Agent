# date_utils.py
import os
from datetime import datetime, timedelta
import pytz
import dateparser

TZ = pytz.timezone(os.getenv("APP_TIMEZONE", "Asia/Kolkata"))

def parse_natural_date_range(text: str):
    """
    Returns (start_dt, end_dt) in timezone-aware datetimes.
    Examples:
      "yesterday" -> yesterday 00:00 to 23:59:59.999999
      "last week" -> last Monday..Sunday (7 days)
      "today"     -> today 00:00..now
    Fallback: 7 days window ending now.
    """
    now = datetime.now(TZ)

    text_norm = (text or "").strip().lower()
    if "yesterday" in text_norm:
        day = (now - timedelta(days=1)).date()
        start = TZ.localize(datetime.combine(day, datetime.min.time()))
        end   = TZ.localize(datetime.combine(day, datetime.max.time()))
        return start, end

    if "last week" in text_norm:
        # last week Mon..Sun (relative to locale Mon=0)
        this_monday = (now - timedelta(days=now.weekday())).date()
        last_monday = this_monday - timedelta(days=7)
        last_sunday = last_monday + timedelta(days=6)
        start = TZ.localize(datetime.combine(last_monday, datetime.min.time()))
        end   = TZ.localize(datetime.combine(last_sunday, datetime.max.time()))
        return start, end

    if "this week" in text_norm or "current week" in text_norm:
        this_monday = (now - timedelta(days=now.weekday())).date()
        start = TZ.localize(datetime.combine(this_monday, datetime.min.time()))
        end   = now
        return start, end

    if "today" in text_norm:
        day = now.date()
        start = TZ.localize(datetime.combine(day, datetime.min.time()))
        end   = now
        return start, end

    # Generic dateparser fallback (e.g., "Nov 3", "Oct 28 - Nov 3")
    result = dateparser.parse(text_norm, settings={"TIMEZONE": str(TZ), "RETURN_AS_TIMEZONE_AWARE": True})
    if result:
        start = result.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = result.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end

    # default: last 7 days
    start = now - timedelta(days=7)
    return start, now
