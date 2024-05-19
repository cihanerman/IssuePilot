# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set environment varibles
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set work directory
WORKDIR /usr/src/app

RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    python3-dev \
    gcc \
    musl-dev

RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run the application:
CMD ["sh", "-c", "python manage.py migrate && gunicorn IssuePilot.wsgi:application -w 3 -b '0.0.0.0:8000'"]