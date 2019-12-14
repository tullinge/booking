# Booking

[![Build Status](https://travis-ci.org/tullinge/booking.svg?branch=master)](https://travis-ci.org/tullinge/booking)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tullinge/booking.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tullinge/booking/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/tullinge/booking.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tullinge/booking/alerts/)

A booking system for the yearly event **Allaktivitetsdag** at Tullinge gymnasium.

## Requirements

- Docker & docker-compose
- Python 3
- Python libraries (look in `requirements.txt`)

### Instructions (running locally)

1. `docker-compose up -d`
2. `python scripts/setup_db.py`
3. `python scripts/insert_demo_data.py`
4. `python main.py`
   
### Instructions (deployment)

1. Set `DOCKER_HOST` and `MYSQL_PASSWORD`
2. `docker-compose -f docker-compose.yml -f prod.yml up`
3. `docker exec booking_app_1 python scripts/setup_db.py`
4. `docker exec -it booking_app_1 python scripts/code_generator.py` ???

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
