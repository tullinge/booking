import sys
sys.path.append('../')

from components.db import sql_query

if __name__ == "__main__":
    sql_query("DROP TABLE activities")
    sql_query("DROP TABLE questions")
    sql_query("DROP TABLE options")
    sql_query("DROP TABLE answers")
    sql_query("DROP TABLE admins")
    sql_query("DROP TABLE students")
