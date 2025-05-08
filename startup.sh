#!/bin/bash
# Create necessary directories
mkdir -p downloads/audio
mkdir -p downloads/video
mkdir -p outputs
mkdir -p uploads
mkdir -p "youtube audio"

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT app:app