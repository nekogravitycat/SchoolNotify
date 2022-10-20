FROM python:3.10.8-slim-buster
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD gunicorn src.website:app
