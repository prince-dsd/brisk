# Use Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies from pyproject.toml
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-dev --no-interaction

# Copy the rest of the application code
COPY . /app/

# Expose port 8000 for Django app
EXPOSE 8000

# Run the Django app using Gunicorn
CMD ["gunicorn", "railway_project.wsgi:application", "--bind", "0.0.0.0:8000"]
