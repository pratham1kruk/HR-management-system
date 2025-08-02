# Use an official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

HEALTHCHECK CMD curl --fail http://localhost:5000/ || exit 1


# Copy project files
COPY backend/ ./    
# Copy Flask app
COPY db_init/ /app/db_init
CMD ["gunicorn", "app:app", "--chdir", "/app", "--bind", "0.0.0.0:5000"]
