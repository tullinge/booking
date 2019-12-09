from flask import Blueprint, render_template, redirect ,request

# blueprint init
student_routes = Blueprint(
    "student_routes",
    __name__,
    template_folder="../templates"
)

@student_routes.route("/login", methods=["GET", "POST"])
def students_login():
    if request.method == "GET":
        return render_template("student/login.html")
    else:
        password = request.form["password"]
        
        # perform validation, login etc...
        if not password:
            return render_template("student/login.html", fail="Saknar variabler."), 400

        # check if correct etc....

        # if come this far, we'll redirect to the /setup page
        return redirect("/setup")


@student_routes.route("/setup")
# @login_required <-- should be decorator
def setup():
    return render_template("student/setup.html")

@student_routes.route("/activities")
# @login_required <-- should be decorator
def activities():
    return render_template("student/activities.html")

@student_routes.route("/confirmation")
# @login_required <-- should be decorator
def confirmation():
    return render_template("student/confirmation.html")