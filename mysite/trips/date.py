from datetime import datetime, timedelta


def next_weekday(dt: datetime, weekday: int = 0) -> datetime:
    """Get the datetime for an upcoming weekday. 0 = Monday, 1=Tuesday, 2=Wednesday..."""

    days_ahead = weekday - dt.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return dt + timedelta(days_ahead)
