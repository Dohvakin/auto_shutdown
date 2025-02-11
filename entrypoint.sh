#!/bin/bash
echo "TRUENAS_HOST=$TRUENAS_HOST" > /usr/src/app/env_file
echo "TRUENAS_USERNAME=$TRUENAS_USERNAME" >> /usr/src/app/env_file
echo "TRUENAS_PASSWORD=$TRUENAS_PASSWORD" >> /usr/src/app/env_file
echo "USE_SSL=$USE_SSL" >> /usr/src/app/env_file
echo "INTERVAL_CHECK_ENABLED=$INTERVAL_CHECK_ENABLED" >> /usr/src/app/env_file

# Now exec the original CMD (which presumably starts cron)
chmod 0755 /usr/src/app/env_file
cat /usr/src/app/env_file >> /etc/environment
exec "$@"
