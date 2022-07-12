#!/bin/bash
echo $(date)
python3 /app/updater.py noNotifications
python3 /app/vaccine.py