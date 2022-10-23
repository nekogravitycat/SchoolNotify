FROM python:3.10.8
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b 0.0.0.0:80", "src.website:app"]
