import os
import re
from secret import *

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/kinkstruction"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# with open(".secret") as f:
#     for line in f:
#         line = line.strip()
#         if not re.match("^\s*$", line):
#             key, val = re.split(r"\s*=\s*", line, maxsplit=1)
#             os.environ[key] = str(val)
#
# SECRET_KEY = os.environ["SECRET_KEY"]
# ITSDANGEROUS_SECRET_KEY = os.environ["ITSDANGEROUS_SECRET_KEY"]


USER_ROLES = {
    "User": 0,
    "Admin": 1
}
