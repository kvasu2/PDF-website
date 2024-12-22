#!/bin/sh
python3 setup_db.py
exec gunicorn --workers 1 --bind 0.0.0.0:8000 wsgi:app
