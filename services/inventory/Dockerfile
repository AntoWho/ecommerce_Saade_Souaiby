# Use a base image with Python
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY services/inventory/inventory.py .
COPY database/database.py ./database/database.py

# Expose the port used by this service
EXPOSE 5002

# Run the application
CMD ["python", "inventory.py"]
