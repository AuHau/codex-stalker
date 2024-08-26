from os import environ

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": environ.get('DB', 'database.db'),
    }
}

INSTALLED_APPS = [
    'stalker',
]
