# Use an official Python image as the base
FROM python:3.9

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Cloud Run will use
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]  # Change 'main.py' to your app's entry point
