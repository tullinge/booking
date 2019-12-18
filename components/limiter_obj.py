# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask_limiter import Limiter

# components import
from components.core import get_client_ip

limiter = Limiter(key_func=get_client_ip)
