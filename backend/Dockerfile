# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install Poetry
RUN apt-get update \
    && apt-get install curl jq -y \
    && curl -sSL https://install.python-poetry.org | python - --version 1.4.2

ENV PATH="/root/.local/bin:$PATH"

# Use Poetry to install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi
