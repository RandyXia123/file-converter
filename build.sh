#!/bin/bash
apt-get update || true
apt-get install -y tesseract-ocr || true
export PATH=$PATH:/usr/bin:/usr/local/bin