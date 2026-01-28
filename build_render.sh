#!/bin/bash
# Build script for Render deployment
# This script is run during the build phase on Render

echo "========================================="
echo "Installing system dependencies..."
echo "========================================="

# Note: On Render's free tier, you cannot install system packages
# using apt-get. FFmpeg should be available on Render's Python runtime.
# If it's not, video processing may fail.

echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg found: $(ffmpeg -version | head -n 1)"
else
    echo "WARNING: FFmpeg not found. MoviePy may not work correctly."
    echo "Video processing features will be disabled."
fi

echo ""
echo "========================================="
echo "Installing Python dependencies..."
echo "========================================="

# Install Python dependencies
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
