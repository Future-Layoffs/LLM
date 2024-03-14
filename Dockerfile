# Use Python Alpine base image
FROM python:3.11-alpine


# Install gcc (and other system dependencies if needed)
RUN apt-get update && apt-get install -y gcc

# Set the working directory in the container
WORKDIR /app

# Copy only the files necessary for installing dependencies to avoid cache invalidation
COPY poetry.lock pyproject.toml /app/

# Install Poetry
RUN pip install poetry

# Configure Poetry to install dependencies globally (not in a virtual environment)
# and then install dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the rest of your application
COPY . /app/

# Command to run your application
CMD ["python", "main.py"]
