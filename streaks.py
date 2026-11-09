from datetime import timedelta

def calculate_streak(days, today):
    """days is a set of 'YYYY-MM-DD' strings; today is a date."""
    current = today
    if current.isoformat() not in days:
        current -= timedelta(days=1)
    streak = 0
    while current.isoformat() in days:
        streak += 1
        current -= timedelta(days=1)
    return streak