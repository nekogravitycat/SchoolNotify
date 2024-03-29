FROM python:3.12.1-slim
COPY . /app
WORKDIR /app
RUN mkdir log
RUN mkdir data
RUN pip install -r requirements.txt
CMD gunicorn -b 0.0.0.0:5000 src.website:app
