import string

allowed_characters = string.printable + ["å", "ä", "ö", "Å", "Ä", "Ö"]

def contains_illegal_characters(variable):
    if any(x not in allowed_characters for x in variable):
        return True

    return False

