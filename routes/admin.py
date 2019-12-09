# tullinge/booking
# https://github.com/tullinge/booking

from flask import Blueprint, render_template, request, redirect
from components.core import letter_check

# blueprint init
admin_routes = Blueprint("admin_routes", __name__, template_folder="../templates")

BASEPATH = "/admin"


@admin_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
    elif request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        # perform validation, login etc...
        if not username or not password:
            return render_template("admin/login.html", fail="Saknar variabler."), 400

        if len(username) >= 255 or len(password) >= 255:
            return render_template("admin/login.html", fail="För lång input."), 400

        if len(password) <= 4:
            return render_template("admin/login.html", fail="För kort lösenord."), 400

        if letter_check(username) or letter_check(password):
            return render_template("admin/login.html", fail="Icke tillåtna kaktärer."),400

        # if validation has come this far, user should be authenticated
        return redirect(f"{BASEPATH}/")


# ----------Loged in----------
#   Mani loged in page
@admin_routes.route("/")
def index():
    return render_template("admin/index.html")


#   activitys control page
@admin_routes.route("/activities")
def activities():
    return render_template("admin/activities.html")


#   Admin control page
@admin_routes.route("/admins")
def admin_users():
    return render_template("admin/admin_users.html")


@admin_routes.route("/lists")
def lists():
    return render_template("admin/lists.html")
