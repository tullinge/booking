import sys

sys.path.append("../")

from components.db import sql_query

sql_query(
    """
        INSERT INTO `students` (`id`, `password`) 
            VALUES (1, "DEVBEAR1");
    """
)
