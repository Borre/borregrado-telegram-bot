FROM python:3.9-alpine

# Install system dependencies
RUN apk update && apk add gcc musl-dev mariadb-connector-c-dev bind-tools
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Run the Telegram bot
CMD ["python", "app.py"]
