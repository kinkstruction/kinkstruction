import os
import re

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/kinkstruction"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

with open(".secret") as f:
    for line in f:
        line = line.strip()
        key, val = re.split(r"\s*=\s*", line, maxsplit=1)
        os.environ[key] = str(val)

SECRET_KEY = os.environ["SECRET_KEY"]

USER_ROLES = {
    0: "User",
    1: "Admin"
}
