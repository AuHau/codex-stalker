import codex_client
import locale
import os
from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, '')


def get_reward(ask: codex_client.StorageAsk) -> int:
    return int(ask.duration) * int(ask.reward)


def format_size(size) -> str:
    try:
        size = int(size)
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        for unit in units[::-1]:
            if size >= pow(1024, units.index(unit)):
                return "%3.1f %s" % (size / pow(1024, units.index(unit)), unit)
    except ValueError:
        return "Invalid input. Please enter a number."


def format_duration(duration) -> str:
    try:
        duration = int(duration)

        future_time = datetime.now() + timedelta(seconds=duration)
        return future_time.strftime('%c')
    except ValueError:
        return "Invalid input. Please enter a number."


def format_id(id) -> str:
    if os.environ.get("FULL_IDS") is not None:
        return id

    return f"{id[:5]}...{id[-3:]}"
