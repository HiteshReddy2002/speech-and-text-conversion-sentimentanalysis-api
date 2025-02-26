# Use an official lightweight Python image
FROM python:3.9-slim

# Install ffmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set FFmpeg paths explicitly for Pydub
ENV PATH="/usr/bin:$PATH"
ENV FFMPEG_PATH="/usr/bin/ffmpeg"
ENV FFPROBE_PATH="/usr/bin/ffprobe"

# Expose the port for Gunicorn
EXPOSE 8080

# Run the application with Gunicorn (Flask/FastAPI)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
