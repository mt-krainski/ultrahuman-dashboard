from datetime import datetime, timedelta


def format_timedelta(td: timedelta) -> str:
    """Format a timedelta as hours and minutes."""
    total_minutes = int(td.total_seconds() // 60)
    sign = "-" if total_minutes < 0 else ""
    total_minutes = abs(total_minutes)
    hours, minutes = divmod(total_minutes, 60)
    if hours > 0:
        return f"{sign}{hours}h {minutes}m"
    else:
        return f"{sign}{minutes}m"


def format_time(dt: datetime) -> str:
    """Format datetime as hours and minutes."""
    return dt.strftime("%H:%M")
