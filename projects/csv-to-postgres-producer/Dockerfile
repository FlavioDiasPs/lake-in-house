# Use official Python runtime as base image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY csv-to-postgres-producer /app

# Install uv (and any dependencies)
RUN pip install uv

# Run the application
CMD ["uv", "run", "src/main.py"]
