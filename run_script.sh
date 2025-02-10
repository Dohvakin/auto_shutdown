#!/bin/bash
echo "TRUENAS_HOST=$TRUENAS_HOST"
echo "TRUENAS_USERNAME=$TRUENAS_USERNAME"
echo "TRUENAS_PASSWORD=$TRUENAS_PASSWORD"
echo "USE_SSL=$USE_SSL"
echo "INTERVAL_CHECK_ENABLED"=$INTERVAL_CHECK_ENABLED

/usr/bin/python /usr/src/app/shutdown_script.py >> /usr/src/app/logs/shutdown_script.log