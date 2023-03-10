#!/bin/sh
gunicorn --chdir app 'app:create_app()' -w 2 --threads 2 -b 0.0.0.0:8080
