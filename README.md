# Booking

[![Build Status](https://travis-ci.com/tullinge/booking.svg?branch=master)](https://travis-ci.com/tullinge/booking)
[![Dependencies](https://img.shields.io/librariesio/github/tullinge/booking)](https://libraries.io/github/tullinge/booking)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tullinge/booking.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tullinge/booking/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/tullinge/booking.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tullinge/booking/alerts/)
[![Total lines](https://tokei.rs/b1/github/tullinge/booking)](https://github.com/tullinge/booking)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A booking system for the yearly event **Allaktivitetsdag** at Tullinge gymnasium.

Demo site at [allaktivitetsdagen.tullingelabs.se](http://allaktivitetsdagen.tullingelabs.se/login)

## Requirements

- Docker & docker-compose
- Python 3
- Python libraries (look in `requirements.txt`)

### Instructions (running locally)

1. `docker-compose up -d`
2. `python scripts/setup_db.py`
3. `python scripts/create_admin.py`
4. `python main.py`

### Instructions (deployment)

1. Set `DOCKER_HOST` and `MYSQL_PASSWORD`
2. `docker-compose -f docker-compose.yml -f prod.yml up -d`
3. `docker exec booking_app_1 python scripts/setup_db.py`
4. `docker exec -it booking_app_1 python scripts/create_admin.py`

## Navigating the interface

Once you got the webserver running and an initial admin account created, you can log in to the admin interface by visiting `/admin`.

Once logged in, go ahead and click `Aktiviteter` in order to create new activities.  From each activity, you can create questions that the students have to answer when choosing the activity.

Then you can move on to the `Klasser` page, where you can create school classes that will be shown to the students when they initially set up their accounts.

Finally, you can then move on to the `Elever` page in order to create new codes. Newly generated codes are anonymous, so they can be given out to any school class. When a student logs in using a code for the first time, they will be able to enter their first- and surname along with choosing their class.

When the student has the account setup, they can browse available activities, book activities, and re-book to other activities if they change their mind.

## User stories

- As a **student** I want to be able to **login with my code**
- As a **logged in student** I want to be able to **browse activities**
- As a **logged in student** I want to be able to **register with my firstname, lastname, activity and class**
- As a **registered student** I want to be able to **see a confirmation of my choices**

---

- As a **student who have already registered** I want to be able to **restart and update my choices**

---

- As a **admin** I want to be able to **login with my username and password**
- As a **logged in admin** I want to be able to **get a list of codes** so that I can **hand them out to class mentors**
- As a **logged in admin** I want to be able to **get a list of registered users per activity** so that I can **inform activity leaders**
- As a **logged in admin** I want to be able to **get a list of registered users per class** so that I can **inform class mentors**
- As a **logged in admin** I want to be able to **regster new admins**
- As a **logged in admin** I want to be able to **remove old admins**
- As a **logged in admin** I want to be able to **change password and username**

## Other requirements

- There should be a limit of available spots per activity
- Students who are registering for **bowling** should be able to select if they want food or not

## Contributing

Feel free to open an issue or send in a pull request. All code should be formatted using [black](https://github.com/psf/black). This project uses the semantic versioning convention, see [CHANGELOG.md](CHANGELOG.md) for more information.
