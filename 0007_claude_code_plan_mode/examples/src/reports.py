from datetime import date


def daily_filename(day: date) -> str:
    return f"orders-{day:%Y-%m-%d}.csv"


def hourly_filename(day: date, hour: int) -> str:
    return f"orders-{day:%Y-%m-%d}-{hour:02}.csv"
