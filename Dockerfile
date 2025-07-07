# Use an official Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (to leverage Docker cache)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Optional: Expose the port used by FastAPI
EXPOSE 8000

# Command to run FastAPI via uvicorn
CMD bash -c "python -m app.api.api_runner & python -m app.batch_processing.daemon"
