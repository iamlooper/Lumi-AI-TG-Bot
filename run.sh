#!/bin/sh

# Start a virtual environment.
if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d "$HOME/VIC-TG-Bot-venv" ]; then
        python3 -m venv "$HOME/VIC-TG-Bot-venv"
    fi
    source "$HOME/VIC-TG-Bot-venv/bin/activate"
fi

# Install requirements.
pip -q install -r requirements.txt

# Start app.
python3 -m app