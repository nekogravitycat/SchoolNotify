#!/bin/bash
cd /app
echo "run_daily.sh run at $(date)"
/usr/local/bin/python /app/src/daily.py
echo "run_daily.sh finish at $(date)"
