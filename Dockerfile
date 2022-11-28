FROM python:3.11.0-slim
RUN apt update && apt install -y cron
COPY . /app
WORKDIR /app
RUN mkdir log
RUN chmod 0644 ./crontab-job
RUN crontab ./crontab-job
RUN pip install -r requirements.txt
CMD cron && gunicorn -b 0.0.0.0:5000 src.website:app
