# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for audio
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils \
    pulseaudio \
    libsndfile1 \
    software-properties-common \
    libportaudio2 \
    libasound2-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Configure ALSA and PulseAudio (optional)
ENV PULSE_SERVER=/run/pulse/native
ENV PULSE_RUNTIME_PATH=/run/user/1000

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py"]
