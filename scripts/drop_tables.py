# tullinge/booking
# https://github.com/tullinge/booking

import sys
from pathlib import Path

# Add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from components.db import sql_query


def drop(query, name=None):
    try:
        sql_query(query)
    except Exception:
        print(f"table {name} doesn't exist")


if __name__ == "__main__":
    drop("DROP TABLE activities", name="activities")
    drop("DROP TABLE questions", name="questions")
    drop("DROP TABLE options", name="options")
    drop("DROP TABLE answers", name="answers")
    drop("DROP TABLE admins", name="admins")
    drop("DROP TABLE students", name="students")
    drop("DROP TABLE school_classes", name="school_classes")
    drop("DROP TABLE leaders", name="leaders")
    drop("DROP TABLE settings", name="settings")
