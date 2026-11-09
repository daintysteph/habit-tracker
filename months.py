import calendar


def month_weeks(year, month):
    """Weeks of the month, Monday first. Each week has 7 numbers; 0 means 'not in this month'."""
    return calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)


def shift_month(year, month, delta):
    """Move forward or back by delta months, e.g. (2026, 12, +1) -> (2027, 1)."""
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1
