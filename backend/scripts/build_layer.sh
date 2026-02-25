#!/bin/bash
# Build script for Lambda Layer containing scraper and analytics modules

set -e

echo "Building shared Lambda Layer..."

# Create layer directory
LAYER_DIR="layer/python"
mkdir -p "$LAYER_DIR"

# Copy scraper module
echo "Copying scraper module..."
cp -r ../scraper/src "$LAYER_DIR/scraper"

# Copy analytics module
echo "Copying analytics module..."
cp -r ../analytics/src "$LAYER_DIR/analytics"

# Create __init__.py files if they don't exist
touch "$LAYER_DIR/scraper/__init__.py"
touch "$LAYER_DIR/analytics/__init__.py"

# Install dependencies to layer
pip install \
    --platform manylinux2014_x86_64 \
    --target="$LAYER_DIR" \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: \
    numpy httpx beautifulsoup4 tenacity

echo "Layer built successfully!"
echo "Layer contents:"
ls -la "$LAYER_DIR"
