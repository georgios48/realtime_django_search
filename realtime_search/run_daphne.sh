#!/bin/zsh

# Load environment variables
export DJANGO_SETTINGS_MODULE=realtime_search.settings
export PYTHONPATH=.

# Run Daphne server
echo "Starting Daphne server on 127.0.0.1:8000 ..."
daphne -b 127.0.0.1 -p 8000 realtime_search.asgi:application