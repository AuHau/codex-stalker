import os
import requests


def get_ntfy_notifier():
    topic = os.environ.get('NTFY_TOPIC')
    host = os.environ.get('NTFY_HOST', 'https://ntfy.sh')
    user = os.environ.get('NTFY_USER')
    password = os.environ.get('NTFY_PASSWORD')

    if topic is None:
        return None

    def notify(msg):
        auth_kwarg = {'auth': (user, password)} if user and password else {}

        requests.post(
            f"{host}/{topic}",
            headers=dict(title="Codex Stalker Event"),
            data=msg,
            **auth_kwarg,
        )

    return notify
