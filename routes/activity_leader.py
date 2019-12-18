# tullinge/booking
# https://github.com/tullinge/booking

from flask import Blueprint, render_template, jsonify, request, session, redirect

from components.db import dict_sql_query
from components.google import google_login
from components.decorators import activity_leader_login_required

# blueprint init
activity_leader_routes = Blueprint(
    "activity_leader_routes", __name__, template_folder="../templates"
)

BASEPATH = "/leader"


@activity_leader_routes.route("/")
@activity_leader_login_required
def index():
    # fetch activities leader has access to
    query = dict_sql_query(
        f"SELECT activity_id FROM leaders WHERE email='{session.get('leader_email')}'"
    )

    activities = []
    for obj in query:
        students = []

        # get questions
        questions = dict_sql_query(
            f"SELECT * FROM questions WHERE activity_id={obj['activity_id']}"
        )

        # students that selected this activity
        for student in dict_sql_query(
            f"SELECT * FROM students WHERE chosen_activity={obj['activity_id']}"
        ):
            # build answers
            answers = []
            for question in questions:
                answer = dict_sql_query(
                    f"SELECT * FROM answers WHERE question_id={question['id']} AND student_id={student['id']}",
                    fetchone=True,
                )

                if not answer:
                    answers.append()
                else:
                    if not question["written_answer"]:
                        answers.append(
                            dict_sql_query(
                                f"SELECT text FROM options WHERE id={answer['option_id']}",
                                fetchone=True,
                            )["text"]
                        )
                    else:
                        answers.append(answer["written_answer"])

            students.append(
                {
                    "student": student,
                    "class_name": dict_sql_query(
                        f"SELECT class_name FROM school_classes WHERE id={student['class_id']}",
                        fetchone=True,
                    )["class_name"],
                    "answers": answers,
                }
            )

        # add to list
        activities.append(
            {
                "name": dict_sql_query(
                    f"SELECT name FROM activities WHERE id={obj['activity_id']}",
                    fetchone=True,
                )["name"],
                "students": students,
                "questions": questions,
            }
        )

    return render_template("leader/index.html", activities=activities)


@activity_leader_routes.route("/login")
def login():
    return render_template("leader/login.html")


@activity_leader_routes.route("/callback", methods=["POST"])
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
    leader = dict_sql_query(
        f"SELECT * FROM leaders WHERE email='{data['email']}'", fetchone=True
    )

    if not leader:
        return jsonify({"status": False, "code": 400, "message": "User is not leader."})

    session["leader_logged_in"] = True
    session["leader_id"] = leader["id"]
    session["leader_email"] = leader["email"]

    return (
        jsonify({"status": True, "code": 200, "message": "authenticated"}),
        200,
    )


@activity_leader_routes.route("/callback/error", methods=["POST"])
def callback_error():
    return render_template(
        "callback_error.html",
        message=request.form.get("message"),
        redirect_basepath="/leader",
    )


# logout
@activity_leader_routes.route("/logout")
@activity_leader_login_required
def logout():
    """
    Leader logout

    * destory user session (GET)
    """

    session.pop("leader_logged_in", False)
    session.pop("leader_id", None)
    session.pop("leader_email", None)

    return redirect(f"{BASEPATH}/login")
