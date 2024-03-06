#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Navigate to the plugins directory
cd plugins

# Iterate over each plugin directory and install it
for plugin in */ ; do
    echo "Installing plugin: $plugin"
    pip install -e "$plugin"
done
