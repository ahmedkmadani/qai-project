# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set database environment variables
ENV DATABASE_NAME=your_database_name
ENV DATABASE_USER=your_database_user
ENV DATABASE_PASSWORD=your_database_password
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=5432
ENV OPENAI_API_KEY=your_openai_api_key

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Start the Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "qai.wsgi:application"]
