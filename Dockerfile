# Use Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Set environment variables for Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies from pyproject.toml
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-interaction --without dev --no-root

# Copy the rest of the application code
COPY . /app/

# Expose port 8000 for Django app
EXPOSE 8000

# Run the Django app using Gunicorn
CMD ["gunicorn", "ticket_system.wsgi:application", "--bind", "0.0.0.0:8000"]
