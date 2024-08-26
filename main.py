import django
import os, sys, inspect

sys.path.append(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

# Django setting up
os.environ["DJANGO_SETTINGS_MODULE"] = "stalker.settings"
django.setup()

from stalker import watcher, notifiers

node_url = os.environ.get('CODEX_API_URL', 'http://localhost:8080/')
poll_interval = int(os.environ.get('POLL_INTERVAL', '5'))
notifications = notifiers._get_notifiers()

try:
    watcher.watch_loop(node_url, notifications, poll_interval)
except KeyboardInterrupt:
    print("Exiting Stalker")
