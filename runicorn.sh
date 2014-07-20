#!/usr/bin/env bash

gunicorn run:app --log-file=- --bind="localhost:5000"
