#! /usr/bin/env bash

while ! nc -z mysql 3306; do echo "waiting for mysql..." && sleep 3; done

echo "Running db scripts"
python scripts/setup_db.py
python scripts/insert_demo_data.py

gunicorn app:app -b 0.0.0.0:8000 --worker-tmp-dir /dev/shm
