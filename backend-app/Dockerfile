# Dockerfile untuk Backend (Flask)
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000 

# Run the application directly (no shell needed)
CMD ["python", "app.py"]
