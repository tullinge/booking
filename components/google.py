# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask import jsonify

from google.oauth2 import id_token
from google.auth.transport import requests

import requests as requests_module

from os import environ

GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", default=False)
GSUITE_DOMAIN_NAME = environ.get("GSUITE_DOMAIN_NAME", default=False)
MENTOR_GSUITE_DOMAIN_NAME = environ.get("MENTOR_GSUITE_DOMAIN_NAME", default=False)


def google_login(token, hd_name):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )

        # check for valid iss
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return {
                "status": False,
                "resp": (
                    jsonify(
                        {"status": False, "code": 400, "message": "Invalid issuer."}
                    ),
                    400,
                ),
            }

        # if auth request is from a G Suite domain:
        if hd_name and "hd" not in idinfo:
            return {
                "status": False,
                "resp": (
                    jsonify(
                        {
                            "status": False,
                            "code": 400,
                            "message": "User is not using hosted email, please use your school address.",
                        }
                    ),
                    400,
                ),
            }

        if hd_name and idinfo["hd"] != hd_name:
            return {
                "status": False,
                "resp": (
                    jsonify(
                        {
                            "status": False,
                            "code": 400,
                            "message": "Wrong hosted domain, please use your school address.",
                        }
                    ),
                    400,
                ),
            }

    except ValueError:
        # Invalid token
        return {
            "status": False,
            "resp": (
                jsonify({"status": False, "code": 400, "message": "Invalid token.",}),
                400,
            ),
        }

    # user signed in
    r = requests_module.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")

    if r.status_code is not requests_module.codes.ok:
        return {
            "status": False,
            "resp": (
                jsonify(
                    {
                        "status": False,
                        "code": 500,
                        "message": "Could not verify token.",
                    }
                ),
                500,
            ),
        }

    data = r.json()

    # verify
    if data["aud"] != GOOGLE_CLIENT_ID:
        return {
            "status": False,
            "resp": (
                jsonify(
                    {"status": False, "code": 400, "message": "'aud' is invalid!",}
                ),
                400,
            ),
        }

    # if all good
    return {"status": True, "resp": {"data": data, "idinfo": idinfo,}}
