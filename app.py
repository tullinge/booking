from flask import Flask, render_template

# import session
from flask_session.__init__ import Session

# import blueprints
from routes.admin import admin_routes
from routes.student import student_routes

# import db config
from db_config import DB_Name, DB_Password, DB_Server, DB_Username

app = Flask(__name__)

# error routes
@app.errorhandler(400)
def error_400(e):
    return render_template("errors/400.html"), 400

@app.errorhandler(404)
def error_404(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(405)
def error_405(e):
    return render_template("errors/405.html"), 405

@app.errorhandler(500)
def error_500(e):
    return render_template("errors/500.html"), 500

# session setup
SESSION_TYPE = "sqlalchemy"
SESSION_SQLALCHEMY = f'mysql+pymysql://{DB_Username}{DB_Password}@{DB_Server}/{DB_Name}'

SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

app.config.from_object(__name__)
Session(app)

# register blueprints
app.register_blueprint(admin_routes, url_prefix="/admin")
app.register_blueprint(student_routes, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
