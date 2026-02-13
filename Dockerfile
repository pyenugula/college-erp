# Use a correct base image
FROM python:3.12-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Apply database migrations
RUN python3 manage.py migrate

# Expose the port for the Django app
EXPOSE 8000

# Start the Django development server on all available interfaces, port 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

