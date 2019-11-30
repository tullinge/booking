import string
import time

from dconfig import DB_Name, DB_Password, DB_Server, DB_Username
from flask import Flask, redirect, render_template, request, template_rendered, url_for
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder=".")

app.config["MYSQL_HOST"] = DB_Server
app.config["MYSQL_USER"] = DB_Username
app.config["MYSQL_PASSWORD"] = DB_Password
app.config["MYSQL_DB"] = DB_Name

mysql = MySQL(app)

allowed_characters = string.printable + ["å", "ä", "ö", "Å", "Ä", "Ö"]


def contains_illegal_characters(variable):
    if any(x not in allowed_characters for x in variable):
        return True

    return False


@app.route("/student_login", methods=["GET", "POST"])
def students_login():
    if request.method == "GET":
        return render_template("student_login.html")
    else:
        username = request.form["usercode"].upper()
        if username == "BEAR":
            return render_template("student_signup.html")
        else:
            pass


@app.route("/student_signup")
def student_signup():
    return render_template("student_signup.html")


if __name__ == "__main__":
    app.run(debug=True)
