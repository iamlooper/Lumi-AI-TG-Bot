#!/bin/bash

# Start venv.
if [ -d "$PWD/venv" ]; then
    source "$PWD/venv/bin/activate"
fi

# Install requirements.
pip install -r requirements.txt --no-cache-dir

# For UB Core to find modules
# Don't Change unless vic dir is renamed
export WORKING_DIR=vic

# Start the app.
python -m vic