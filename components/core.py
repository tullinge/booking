# tullinge/booking
# https://github.com/tullinge/booking

import string

def letter_check(input):
    allowed_characters = string.ascii_letters + string.digits + ["å", "ä", "ö", "Å", "Ä", "Ö"]

    if any(x not in allowed_characters for x in input):
        return True
        
    return False

