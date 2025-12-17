# Code-Critique AI Analysis Tool

FROM python:3.11-slim

# Build argument for AI provider (required: anthropic or openai)
ARG AI_PROVIDER

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/code-critique

# Install common Python dependencies
RUN pip install --no-cache-dir \
    jinja2 \
    jsonschema \
    requests

# Install provider-specific package based on build argument
RUN if [ "$AI_PROVIDER" = "anthropic" ]; then \
        pip install --no-cache-dir anthropic; \
    elif [ "$AI_PROVIDER" = "openai" ]; then \
        pip install --no-cache-dir openai; \
    else \
        echo "Invalid AI_PROVIDER: $AI_PROVIDER. Must be 'anthropic' or 'openai'" && exit 1; \
    fi

# Copy code-critique framework
COPY . /app/code-critique/

# Create reports directory
#RUN mkdir -p /app/code-critique/reports

# Set working directory
WORKDIR /app/code-critique
