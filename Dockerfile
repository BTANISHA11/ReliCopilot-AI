# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .

# Expose ports
EXPOSE 8000 8501

# Default command
CMD ["python", "api.py"]
