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

TASK_STATUSES = {
    0: "Not Started",
    1: "Started",
    2: "Completed, not yet accepted",
    3: "Accepted",
    4: "Rejected"
}

# Pagination settings
NUM_MESSAGES_PER_PAGE = 3
NUM_FRIENDS_PER_PAGE = 3
NUM_TASKS_PER_PAGE = 3
NUM_TASK_POSTS_PER_PAGE = 3

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
