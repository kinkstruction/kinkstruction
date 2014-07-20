#!/usr/bin/env bash

gunicorn run-dev:app --log-file=- --bind="localhost:5000"
