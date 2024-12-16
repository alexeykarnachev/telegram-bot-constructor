import arrow


def format_timestamp(timestamp: int | None = None, timezone: str | None = None) -> str:
    dt = arrow.get(timestamp) if timestamp else arrow.now()

    if timezone:
        dt = dt.to(timezone)

    return dt.format("MMM D, YYYY dddd h:mm A")
