from datetime import datetime, timedelta


def next_weekday(dt: datetime, weekday: int = 0) -> datetime:
    """Get the datetime for an upcoming weekday. 0 = Monday, 1=Tuesday, 2=Wednesday..."""

    days_ahead = weekday - dt.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return dt + timedelta(days_ahead)


def duration_display(td: timedelta) -> str:
    # Converts timedelta obj to a human friendly string

    hours, remaining_seconds = divmod(td.seconds, 3600)
    hours += 24 * td.days
    mins = remaining_seconds // 60

    if hours and mins:
        return f"{hours} hr {mins} min"
    if hours and not mins:
        return f"{hours} hr"
    if not hours and mins:
        return f"{mins} min"
