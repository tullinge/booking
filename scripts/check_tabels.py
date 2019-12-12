import sys
from pathlib import Path

# Add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from components.db import sql_query

if __name__ == "__main__":
    print(sql_query("""SELECT * FROM activities"""))
    print(sql_query("""SELECT * FROM questions"""))
    print(sql_query("""SELECT * FROM options"""))
    print(sql_query("""SELECT * FROM answers"""))
    print(sql_query("""SELECT * FROM admins"""))
    print(sql_query("""SELECT * FROM students"""))
    print(sql_query("""SELECT * FROM school_classes"""))
