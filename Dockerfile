# Use an official lightweight Python runtime
FROM python:3.10-slim

# Set system working directory
WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies smoothly
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY app.py .

# Expose backend port
EXPOSE 8000

# Command to fire up the FastAPI app using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
