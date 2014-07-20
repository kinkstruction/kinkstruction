#!/usr/bin/env bash

gunicorn run:app --log-file=- --bind="0.0.0.0:8000" --reload
