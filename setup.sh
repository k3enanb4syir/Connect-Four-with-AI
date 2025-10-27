#!/bin/bash

# This script creates a virtual environment, installs the
# required packages, and then runs the Connect 4 Python script.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the name of the virtual environment directory
VENV_NAME="venv"

echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi

echo "Creating virtual environment '$VENV_NAME'..."
# Create virtual environment
python3 -m venv $VENV_NAME

echo "Activating virtual environment..."
# Source the activation script
source $VENV_NAME/bin/activate

echo "Installing required packages from requirements.txt..."
# Upgrade pip (good practice) and install packages
pip install --upgrade pip
pip install -r requirements.txt

echo "Running the Connect 4 game..."
# Run the python script using the python interpreter from the virtual env
python3 connect4_with_ai.py

echo "Game finished. Deactivating virtual environment."
# Deactivate
deactivate
