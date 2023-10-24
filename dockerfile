# Use an official Python runtime as the parent image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app

RUN apt-get update && apt-get install -y libgdal-dev

RUN apt-get update && apt-get install -y build-essential gcc g++ python3-dev

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

COPY ./data/merged_gdf.parquet /app/data/

# Copy the application to the image's workdir
COPY app.py /app

# Command to run the application
CMD ["gunicorn", "app:server", "-w", "1", "-t", "300", "-b", "0.0.0.0:8080"]