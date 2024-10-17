#!/bin/bash

# Install python packages
echo "Installing python packages..."
pip install -qr requirements.txt

# Start the app
python -m app