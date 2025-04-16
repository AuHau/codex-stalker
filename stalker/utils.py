import codex_api_client
import locale
import os
from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, '')


def get_reward(ask: codex_api_client.StorageAsk) -> float:
    wei_reward = int(ask.duration) * int(ask.slot_size) * int(ask.price_per_byte_per_second)
    return wei_reward / 10e18


def format_size(size) -> str:
    try:
        size = int(size)
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        for unit in units[::-1]:
            if size >= pow(1024, units.index(unit)):
                return "%3.1f %s" % (size / pow(1024, units.index(unit)), unit)
    except ValueError:
        return "Invalid input. Please enter a number."

    return ""


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
