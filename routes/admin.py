from flask import Blueprint, render_template, request

# blueprint init
admin_routes = Blueprint(
    "admin_routes",
    __name__,
    template_folder="../templates"
)

BASEPATH = "/admin"

@admin_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
    else:
        username = request.form["username"].lower()
        password = request.form["password"]

        # perform validation, login etc...
        if not username or not password:
            return render_template("admin/login.html", fail="Saknar variabler."), 400

        # if validation has come this far, user should be authenticated
        return redirect(f"{BASEPATH}/")


@admin_routes.route("/")
def index():
    return render_template("admin/index.html")

@admin_routes.route("/activities")
def activities():
    return render_template("admin/activities.html")

@admin_routes.route("/admins")
def admin_users():
    return render_template("admin/admin_users.html")