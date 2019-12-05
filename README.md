# Booking
A booking system for the yearly event **Allaktivitetsdag** at Tullinge gymnasium.

### Requirements
- Docker
- Python 3
- Python libraries (look in `requirements.txt`)

### Instructions
1. `docker-compose up` starts the database container
2. `python setup_db.py` populates the database with tables etc
3. `python student/student.py` starts the student web app

### User stories
- As a **student** I want to be able to **login with my code**
- As a **logged in student** I want to be able to **browse activities**
- As a **logged in student** I want to be able to **register with my firstname, lastname, activity and class**
- As a **registered student** I want to be able to **see a confirmation of my choices**

---

- As a **student who have already registered** I want to be able to **restart and update my choices**

---

- As an **admin** I want to be able to **get a list of codes** so that I can **hand them out to class mentors**
- As an **admin** I want to be able to **get a list of registered users per activity** so that I can **inform activity leaders**
- As an **admin** I want to be able to **get a list of registered users per class** so that I can **inform class mentors**

### Other requirements
- There should be a limit of available spots per activity
- Students who are registering for **bowling** should be able to select if they want food or not
