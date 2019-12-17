# tullinge/booking
# https://github.com/tullinge/booking

from os import environ

GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", default=False)
GSUITE_DOMAIN_NAME = environ.get("GSUITE_DOMAIN_NAME", default=False)
