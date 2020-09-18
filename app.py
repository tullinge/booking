# tullinge/booking
# https://github.com/tullinge/booking

from os import environ
from flask import Flask, render_template
from flask_minify import minify
from datetime import timedelta
from time import strftime
from version import version, commit_hash

# import limiter
from components.limiter_obj import limiter

# import blueprints
from routes.admin import admin_routes
from routes.student import student_routes
from routes.activity_leader import activity_leader_routes

# components
from components.db import dict_sql_query

# variables
from components.google import GOOGLE_CLIENT_ID, GSUITE_DOMAIN_NAME

# redis
import redis

DEVELOPMENT = True if environ.get("DEVELOPMENT", None) else False

if DEVELOPMENT:
    print("Development mode enabled, lazy security settings!")

# flask application
app = Flask(__name__)

# setup rate limit
app.config[
    "RATELIMIT_STORAGE_URL"
] = f"redis://{environ.get('REDIS_HOST', 'localhost')}"
limiter.init_app(app)

# minify
minify(app=app)

# variables available across all templates
@app.context_processor
def inject_global_variables():
    return dict(
        version=version,
        commit_hash=commit_hash[0:7],
        generation_time=strftime("%Y-%m-%d %H:%M:%S"),
        GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID,
        GSUITE_DOMAIN_NAME=GSUITE_DOMAIN_NAME,
        BOOKING_LOCKED=dict_sql_query(
            "SELECT value FROM settings WHERE identifier='booking_locked'",
            fetchone=True,
        )["value"],
    )


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


@app.errorhandler(429)
def error_429(e):
    return render_template("errors/429.html"), 429


@app.errorhandler(500)
def error_500(e):
    return render_template("errors/500.html"), 500


# session setup
SESSION_TYPE = "redis"
SESSION_REDIS = redis.Redis(host=environ.get("REDIS_HOST", "localhost"), db=0)

SESSION_COOKIE_SECURE = False if DEVELOPMENT else True
SESSION_COOKIE_SAMESITE = None if DEVELOPMENT else "Strict"

SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

SECRET_KEY = environ.get("SECRET_KEY")

app.config.from_object(__name__)

# register blueprints
app.register_blueprint(admin_routes, url_prefix="/admin")
app.register_blueprint(student_routes, url_prefix="/")
app.register_blueprint(activity_leader_routes, url_prefix="/leader")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
