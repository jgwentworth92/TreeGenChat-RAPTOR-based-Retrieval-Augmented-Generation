# Initial Compile Stage
FROM python:3.11-slim-buster AS compile-image

WORKDIR /source

RUN  useradd appuser && \
    chown -R appuser /source

# Copy only requirements.txt first
COPY requirements.txt .

# Create a virtual environment for python3
RUN python3 -m venv /source/venv

# Activate the virtual environment
ENV PATH="/source/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copying the rest of the files
COPY . .
# Copying the plugins directory and install_plugins.sh script

# Execute permission for entrypoint.sh and install_plugins.sh
RUN chmod a+x entrypoint.sh install_plugins.sh

# Execute the script to install all plugins
RUN ./install_plugins.sh

# Or, alternatively, directly use shell commands to install plugins without a script
# RUN for plugin in plugins/*; do pip install -e "$plugin"; done
# Execute permission for entrypoint.sh
RUN chmod a+x entrypoint.sh

# Running setup tools from setup.py
RUN pip install -e .

# Operational Stage
FROM python:3.11-slim-buster AS build-image

WORKDIR /source

# Copy everything from compile-image
COPY --from=compile-image /source /source

# Execute permission for entrypoint.sh
RUN chmod a+x entrypoint.sh

# Create app user for runner and set ownership
RUN useradd appuser && chown -R appuser /source

ENV PYTHONDONTWRITEBYTEsource=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/source/venv/bin:$PATH"

# Switching to our app user
USER appuser

# Set the entrypoint
ENTRYPOINT ["/source/entrypoint.sh"]
