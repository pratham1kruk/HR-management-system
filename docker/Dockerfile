# Use an official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt .

# Replace the wkhtmltopdf install step
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf manually
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get install -f -y \
    && rm wkhtmltox_0.12.6-1.buster_amd64.deb



RUN pip install --upgrade pip && \
    pip install -r requirements.txt

HEALTHCHECK CMD curl --fail http://localhost:5000/ || exit 1


# Copy project files
COPY backend/ ./    
# Copy Flask app
COPY db_init/ /app/db_init
CMD ["gunicorn", "app:app", "--chdir", "/app", "--bind", "0.0.0.0:5000"]
