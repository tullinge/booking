# tullinge/booking
# https://github.com/tullinge/booking

from flask import Blueprint, render_template, jsonify, request, session, redirect

from components.db import sql_query, dict_sql_query
from components.google import google_login
from components.decorators import mentor_login_required

# blueprint init
mentor_routes = Blueprint("mentor_routes", __name__, template_folder="../templates")

BASEPATH = "/mentor"


@mentor_routes.route("/")
@mentor_login_required
def index():
    # fetch classes mentor has access to
    query = dict_sql_query(
        f"SELECT class_id FROM mentors WHERE email='{session.get('mentor_email')}'"
    )

    classes = []
    for obj in query:
        students = []

        for student in dict_sql_query(
            f"SELECT * FROM students WHERE class_id={obj['class_id']}"
        ):
            students.append(
                {
                    "student": student,
                    "activity_name": dict_sql_query(
                        f"SELECT name FROM activities WHERE id={student['chosen_activity']}",
                        fetchone=True,
                    )["name"]
                    if student["chosen_activity"]
                    else "Ej valt",
                }
            )

        classes.append(
            {
                "name": dict_sql_query(
                    f"SELECT class_name FROM school_classes WHERE id={obj['class_id']}",
                    fetchone=True,
                )["class_name"],
                "students": students,
            }
        )

    return render_template("mentor/index.html", classes=classes)


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
    google = google_login(request.json["idtoken"], None)

    if not google["status"]:
        return google["resp"]

    data = google["resp"]["data"]

    # perform some validation against database
    mentor = dict_sql_query(
        f"SELECT * FROM mentors WHERE email='{data['email']}'", fetchone=True
    )

    if not mentor:
        return jsonify({"status": False, "code": 400, "message": "User is not mentor."})

    session["mentor_logged_in"] = True
    session["mentor_id"] = mentor["id"]
    session["mentor_email"] = mentor["email"]

    return (
        jsonify({"status": True, "code": 200, "message": "authenticated"}),
        200,
    )


@mentor_routes.route("/callback/error", methods=["POST"])
def callback_error():
    return render_template(
        "callback_error.html",
        message=request.form.get("message"),
        redirect_basepath="/mentor",
    )


# logout
@mentor_routes.route("/logout")
@mentor_login_required
def logout():
    """
    Mentor logout

    * destory user session (GET)
    """

    session.pop("mentor_logged_in", False)
    session.pop("mentor_id", None)
    session.pop("mentor_email", None)

    return redirect(f"{BASEPATH}/login")
