#!/bin/bash
cd /app
echo "run_daily.sh run at $(date)"
/usr/local/bin/python -m src.daily
echo "run_daily.sh finish at $(date)"
