#!/bin/bash
# This script starts the Streamlit application.
# It ensures that the script is run from the directory where it is located.
cd "$(dirname "$0")"
# Activate the virtual environment and run the streamlit app
./venv/bin/streamlit run app.py
