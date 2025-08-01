FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN pip install rest_framework_simplejwt

COPY . .

CMD gunicorn iou_tracker_backend.wsgi --bind 0.0.0.0:8000