# tullinge/booking
# https://github.com/tullinge/booking

from flask_limiter import Limiter

from components.core import get_client_ip

limiter = Limiter(key_func=get_client_ip)
