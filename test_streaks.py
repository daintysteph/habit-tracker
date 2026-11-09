from datetime import date
from streaks import calculate_streak

TODAY = date(2026, 11, 9)

def test_no_days_gives_zero():
    assert calculate_streak(set(), TODAY) == 0

def test_only_today():
    assert calculate_streak({"2026-11-09"}, TODAY) == 1

def test_only_yesterday_still_counts():
    assert calculate_streak({"2026-11-08"}, TODAY) == 1

def test_three_days_ending_today():
    days = {"2026-11-07", "2026-11-08", "2026-11-09"}
    assert calculate_streak(days, TODAY) == 3

def test_three_days_ending_yesterday():
    days = {"2026-11-06", "2026-11-07", "2026-11-08"}
    assert calculate_streak(days, TODAY) == 3

def test_gap_breaks_the_streak():
    days = {"2026-11-05", "2026-11-06", "2026-11-08", "2026-11-09"}
    assert calculate_streak(days, TODAY) == 2

def test_old_days_only_gives_zero():
    assert calculate_streak({"2026-11-01", "2026-11-02"}, TODAY) == 0

def test_streak_across_month_boundary():
    days = {"2026-10-31", "2026-11-01", "2026-11-02"}
    assert calculate_streak(days, date(2026, 11, 2)) == 3