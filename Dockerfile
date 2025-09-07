# 1️⃣ Use a modern Python image with OpenSSL 1.1.1+ (TLS 1.2 support)
FROM python:3.11-slim

# Install dependencies and CA certificates
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl-dev \
    && update-ca-certificates \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
