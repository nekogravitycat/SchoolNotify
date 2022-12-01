#!/bin/bash
cd /app
CWD="$(pwd)"
echo "$CWD"
python /app/src/daily.py
