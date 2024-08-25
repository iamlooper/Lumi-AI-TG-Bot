#!/bin/bash

# Install python packages
echo "Installing python packages..."
pip install --ignore-installed -qUr requirements.txt

# Start the app
python -m app