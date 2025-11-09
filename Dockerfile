# Use official Python base image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask reportlab pytest

# Expose port
EXPOSE 5000

# Start your app
CMD ["python3", "ACEest_Fitness_API.py"]
