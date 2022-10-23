FROM python:3.10.8
RUN apt update && apt install -y cron
COPY . /app
COPY crontab /etc/cron.d/sn-daily
RUN chmod 0644 /etc/cron.d/sn-daily
RUN crontab /etc/cron.d/sn-daily
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b 0.0.0.0:5000", "src.website:app"]
