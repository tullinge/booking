# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask import Blueprint, render_template, redirect, request, session

# components import
from components.core import letter_check, hash_password
from components.decorators import login_required
from components.db import sql_query

# blueprint init
student_routes = Blueprint("student_routes", __name__, template_folder="../templates")


@student_routes.route("/")
@login_required
def index():
    return render_template("student/index.html")


@student_routes.route("/login", methods=["GET", "POST"])
def students_login():
    if request.method == "GET":
        return render_template("student/login.html")
    else:
        password = request.form["password"]

        if not password:
            return render_template("student/login.html", fail="Saknar lösenord."), 400

        if not len(password) == 8:
            return render_template("student/login.html", fail="Fel längd."), 400

        if not letter_check(password):
            return (
                render_template("student/login.html", fail="Icke tillåtna kaktärer."),
                400,
            )

        # authentication
        student = sql_query(f"SELECT * FROM students WHERE password='{password}'")

        if not student:
            return render_template("student/login.html", fail="Användaren existerar inte/fel lösenord.")

        # means user is authentication
        session["id"] = student[0][0] # has to be changed perhaps
        session["logged_in"] = True

        # if come this far, we'll redirect to the /setup page
        return redirect("/setup")


@student_routes.route("/setup", methods=["POST", "GET"])
@login_required
def setup():
    if request.method == "GET":
        return render_template("student/setup.html")
    elif request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        school_class = request.form["class"]

        if not first_name or not last_name or not school_class:
            return render_template("student/setup.html", fail="Saknar variabler.")

        


@student_routes.route("/activities")
@login_required
def activities():
    return render_template("student/activities.html")


@student_routes.route("/confirmation")
@login_required
def confirmation():
    return render_template("student/confirmation.html")
