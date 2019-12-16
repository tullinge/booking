# tullinge/booking
# https://github.com/tullinge/booking

import functools
import os

from flask import session, Blueprint, make_response, redirect, request

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

ACCESS_TOKEN_URI = "https://www.googleapis.com/oauth2/v4/token"
AUTHORIZATION_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent"
)

AUTHORIZATION_SCOPE = "openid email profile"

AUTH_REDIRECT_URI = os.environ.get(
    "AUTH_REDIRECT_URI", default="http://localhost:5000/"
)
BASE_URI = os.environ.get("BASE_URI", default="http://localhost:5000/")
# CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", default=False)
# CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", default=False)

AUTH_TOKEN_KEY = "auth_token"
AUTH_STATE_KEY = "auth_state"

auth_app = Blueprint("google_auth", __name__)


def is_logged_in():
    return True if AUTH_TOKEN_KEY in session else False


def build_credentials():
    if not is_logged_in():
        raise Exception("User must be logged in")

    oauth2_tokens = session[AUTH_TOKEN_KEY]

    return google.oauth2.credentials.Credentials(
        oauth2_tokens["access_token"],
        refresh_token=oauth2_tokens["refresh_token"],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI,
    )


def get_user_info():
    credentials = build_credentials()

    oauth2_client = googleapiclient.discovery.build(
        "oauth2", "v2", credentials=credentials,
    )

    return oauth2_client.userinfo().get().execute()


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return functools.update_wrapper(no_cache_impl, view)


@auth_app.route("/google/login")
@no_cache
def login():
    oauth_session = OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        scope=AUTHORIZATION_SCOPE,
        redirect_uri=AUTH_REDIRECT_URI,
    )

    uri, state = oauth_session.create_authorization_url(AUTHORIZATION_URL)

    session[AUTH_STATE_KEY] = state
    session.permanent = True

    return redirect(uri, code=302)


@auth_app.route("/google/auth")
@no_cache
def google_auth_redirect():
    request_state = request.args.get("state", default=None, type=None)

    if request_state is not session[AUTH_STATE_KEY]:
        return "invalid state parameter", 401

    oauth_session = OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        scope=AUTHORIZATION_SCOPE,
        state=session[AUTH_STATE_KEY],
        redirect_uri=AUTH_REDIRECT_URI,
    )

    oauth2_tokens = oauth_session.fetch_access_token(
        ACCESS_TOKEN_URI, authorization_response=request.url,
    )

    session[AUTH_TOKEN_KEY] = oauth2_tokens

    return redirect(BASE_URI, code=302)


@auth_app.route("/google/logout")
@no_cache
def logout():
    session.pop(AUTH_TOKEN_KEY, None)
    session.pop(AUTH_STATE_KEY, None)

    return redirect(BASE_URI, code=302)
