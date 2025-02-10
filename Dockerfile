FROM ubuntu

RUN apt-get update && apt-get install -y python3 python3-pip cron procps python-is-python3 python3-websockets python3-requests dos2unix python3-pytzdata python3-tz

WORKDIR /usr/src/app

COPY shutdown_script.py shutdown_script.py
COPY crontab /etc/cron.d/shutdown-crontab
COPY run_script.sh run_script.sh
RUN chmod 0755 run_script.sh
RUN chmod +x shutdown_script.py
RUN chmod 0644 /etc/cron.d/shutdown-crontab
RUN dos2unix /etc/cron.d/shutdown-crontab
RUN crontab /etc/cron.d/shutdown-crontab
RUN mkdir -p /usr/src/app/logs
RUN chmod 755 /usr/src/app/logs

CMD ["cron", "-f"]
