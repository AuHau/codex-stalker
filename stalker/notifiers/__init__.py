from os import environ
from typing import List, Callable
from datetime import datetime

from .ntfy import get_ntfy_notifier


def _get_notifiers() -> List[Callable[[str], None]]:
    notifiers: List[Callable[[str], None]] = []

    ntfy = get_ntfy_notifier()

    if ntfy is not None:
        print("Enabling NTFY.sh notifier")
        notifiers.append(ntfy)

    if environ.get('DISABLE_CONSOLE') is None:
        print("Enabling console notifier")
        notifiers.append(lambda msg: print(f">>> [{datetime.now().strftime("%H:%M")}]  {msg}"))

    if len(notifiers) == 0:
        raise ValueError('No notifiers configured')

    return notifiers
