import sys
from pathlib import Path

# Add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from components.db import sql_query
from components.core import hash_password

name = input("Enter name: ")
username = input("Enter username: ")
password = hash_password(input("Enter password: "))

sql_query(
    f"""
        INSERT INTO admins (name, username, password)
        VALUES ('{name}', '{username}', '{password}')
    """
)
