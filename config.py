import os
import re
from secret import *

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/kinkstruction"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

USER_ROLES = {
    "User": 0,
    "Admin": 1
}

HTTP_500_POEMS = [
"""
There once was a page on Kinkstruction,
Through your monitor you wanted to unction,
But 500, oh noes!
The server has woes!
It cannot fulfill its main function.
""",
"""
The status returned
HTTP 500
Server done fucked up
"""
]
