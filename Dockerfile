# Initial Compile Stage
FROM python:3.11-slim-bookworm AS compile-image

WORKDIR /source

# Install system dependencies including Git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and set file ownership
RUN useradd appuser && \
    chown -R appuser:appuser /source

USER appuser

# Copy only requirements.txt first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .

# Create a virtual environment for python3 within the user's directory
RUN python3 -m venv /source/venv

# Activate the virtual environment
ENV PATH="/source/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copying the rest of the files with the necessary permissions
COPY --chown=appuser:appuser . .

# Ensure entrypoint.sh is executable
RUN chmod +x entrypoint.sh

# Install the application
RUN pip install -e .

# Operational Stage
FROM python:3.11-slim-bookworm AS build-image

WORKDIR /source

# Create app user for the runner and copy over the virtual environment and application code
RUN useradd appuser
COPY --from=compile-image --chown=appuser:appuser /source /source

# Set the appropriate environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/source/venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Set the entrypoint
ENTRYPOINT ["/source/entrypoint.sh"]
