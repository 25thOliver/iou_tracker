FROM python:3.9-slim-buster

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python -m pip install gunicorn  # Explicitly install gunicorn
RUN echo $PYTHONPATH  # Check the Python path
RUN pip list  # List installed packages

COPY . .

CMD gunicorn iou_tracker_backend.wsgi --bind 0.0.0.0:8000