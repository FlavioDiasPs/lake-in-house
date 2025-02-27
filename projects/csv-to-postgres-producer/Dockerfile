# Use official Python runtime as base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY projects\csv-to-postgres-producer /app
COPY projects\sample_data /app

# Install uv (and any dependencies)
RUN pip install uv

# Run the application
CMD ["uv", "run", "projects/csv-to-postgres-producer/src/main.py"]