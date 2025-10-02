import humanize
from datetime import datetime


def relative_time(timestamp):
    return humanize.naturaltime(timestamp)


def relative_date(timestamp):
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    return humanize.naturaldate(timestamp)
