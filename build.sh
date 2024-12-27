#!/usr/bin/env bash
# Install system dependencies
apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx

# Verify tesseract installation
tesseract --version