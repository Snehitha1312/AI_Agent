# tests/test_date_utils.py
from date_utils import parse_natural_date_range

def test_parse_yesterday():
    s, e = parse_natural_date_range("yesterday")
    assert s.tzinfo is not None and e.tzinfo is not None
    assert (e - s).days in (0, 1)  # full day window

def test_parse_last_week():
    s, e = parse_natural_date_range("last week")
    assert s < e
    assert (e - s).days in (6, 7)
