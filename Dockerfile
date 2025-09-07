# 1️⃣ Use a modern Python image with OpenSSL 1.1.1+ (TLS 1.2 support)
FROM python:3.11-slim

# 2️⃣ Install CA certificates for SSL/TLS
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && update-ca-certificates \
    && apt-get clean

# 3️⃣ Set working directory inside container
WORKDIR /app

# 4️⃣ Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy the rest of your code
COPY . .

# 6️⃣ Command to run your bot
CMD ["python", "bot.py"]
