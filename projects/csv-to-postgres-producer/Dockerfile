# Use official Python runtime as base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app/csv-to-postgres-producer

# Copy the application code into the container
COPY projects/csv-to-postgres-producer /app/csv-to-postgres-producer
COPY projects/sample_data /app/sample_data

# Install uv (and any dependencies)
RUN pip install uv
RUN uv sync

# Run the application
CMD ["uv", "run", "main.py"]