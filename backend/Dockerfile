# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Use Poetry to install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Run the application as a Python module
CMD ["python", "-m", "polydash"]