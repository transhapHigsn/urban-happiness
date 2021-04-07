#!/bin/bash

source .venv/bin/activate

export FLASK_APP=tracker/app.py
export FLASK_ENV=development

flask run
