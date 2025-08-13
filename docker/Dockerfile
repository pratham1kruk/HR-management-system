# -----------------------------
# 1️⃣ Base Image
# -----------------------------
FROM python:3.11-slim-bullseye

# -----------------------------
# 2️⃣ Environment Variables
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# -----------------------------
# 3️⃣ Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    wget \
    curl \
    gnupg \
    libjpeg62-turbo \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 4️⃣ Install wkhtmltopdf
# -----------------------------
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6-1.bullseye_amd64.deb || apt-get install -f -y \
    && rm wkhtmltox_0.12.6-1.bullseye_amd64.deb

# Verify wkhtmltopdf installation
RUN wkhtmltopdf --version

# -----------------------------
# 5️⃣ Install Python dependencies
# -----------------------------
COPY backend/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# -----------------------------
# 6️⃣ Copy application files
# -----------------------------
COPY backend/ ./    
COPY db_init/ ./db_init

# -----------------------------
# 7️⃣ Healthcheck
# -----------------------------
HEALTHCHECK CMD curl --fail http://localhost:5000/ || exit 1

# -----------------------------
# 8️⃣ Start Flask app with Gunicorn
# -----------------------------
CMD ["gunicorn", "app:app", "--chdir", "/app", "--bind", "0.0.0.0:5000", "--workers", "4"]
