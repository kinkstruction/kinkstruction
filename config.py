import os
import re

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/kinkstruction"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

with open(".secret") as f:
    for line in f:
        line = line.strip()
        if not re.match("^\s*$", line):
            key, val = re.split(r"\s*=\s*", line, maxsplit=1)
            os.environ[key] = str(val)

SECRET_KEY = os.environ["SECRET_KEY"]
ITSDANGEROUS_SECRET_KEY = os.environ["ITSDANGEROUS_SECRET_KEY"]

MAIL_SERVER = os.environ["MAIL_SERVER"]
MAIL_PORT = int(os.environ["MAIL_PORT"])
MAIL_USE_TLS = True if os.environ["MAIL_USE_TLS"] == "True" else False
MAIL_USE_SSL = True if os.environ["MAIL_USE_SSL"] == "True" else False
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]

USER_ROLES = {
    "User": 0,
    "Admin": 1
}
