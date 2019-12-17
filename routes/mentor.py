# tullinge/booking
# https://github.com/tullinge/booking

from flask import Blueprint, render_template, jsonify, request, session, redirect

from components.db import sql_query, dict_sql_query
from components.google import google_login, MENTOR_GSUITE_DOMAIN_NAME

# blueprint init
mentor_routes = Blueprint("mentor_routes", __name__, template_folder="../templates")

BASEPATH = "/mentor"


@mentor_routes.route("/")
def index():
    return render_template("mentor/index.html")


@mentor_routes.route("/login")
def login():
    return render_template("mentor/login.html")


@mentor_routes.route("/callback", methods=["POST"])
def students_callback():
    if not request.get_json("idtoken"):
        return (
            jsonify({"status": False, "code": 400, "message": "missing form data"}),
            400,
        )

    # verify using separate module
    google = google_login(request.json["idtoken"], MENTOR_GSUITE_DOMAIN_NAME)

    if not google["status"]:
        return google["resp"]

    data = google["resp"]["data"]
    idinfo = google["resp"]["idinfo"]

    # perform some validation against database
    return ""


@mentor_routes.route("/callback/error", methods=["POST"])
def callback_error():
    return render_template(
        "callback_error.html",
        message=request.form.get("message"),
        redirect_basepath="/mentor",
    )


# logout
@mentor_routes.route("/logout")
# @mentor_login_required
def logout():
    """
    Mentor logout

    * destory user session (GET)
    """

    session.pop("mentor_logged_in", False)
    session.pop("mentor_id", None)

    return redirect("/mentor/login")
