# FastAPI Dynamic Plugins Framework

## Description

The FastAPI Dynamic Plugins Framework is designed to provide a secure and scalable infrastructure for JWT token authentication and application functionality extension through a dynamic plugin system. By leveraging Auth0, the framework ensures robust security measures for JWT token management, streamlining the authentication process while maintaining high security standards. Aimed at offering a foundational architecture for FastAPI applications, this framework facilitates easy application customization and scalability through the integration of modular plugins.

## Dynamic Plugin System Overview

This framework features an innovative dynamic plugin system that allows for the delegation of business logic and application functionalities into separate, interchangeable modules known as "plugins". This system enhances application extensibility and customization, enabling developers to add or remove plugins without modifying the core application code.

### How It Works

Plugins are autonomously discovered and loaded from the specified plugin directory. Each plugin should be a self-contained Python package that includes business logic and optionally, API routes. This approach allows for significant flexibility in extending application capabilities.

## Creating a Plugin

Creating a plugin for the FastAPI Dynamic Plugins Framework involves a few structured steps and adherence to a specific organization for each plugin package.

### Plugin Directory Structure

A typical plugin might be structured as follows, assuming `plugin_name` is your plugin's name:

```
plugin_name/
├── setup.py  # Entry point for the plugin, defining installation requirements and metadata.
├── plugin_name/
    ├── __init__.py  # Contains the business logic of the plugin.
    └── routes.py    # Defines API routes specific to the plugin.
```

### Steps to Create a New Plugin

1. **Plugin Setup**: Initialize your plugin directory with the structure outlined above. The top-level directory should match your plugin's name, containing a `setup.py` file and a subdirectory also named after your plugin. This subdirectory will house your business logic and API routes.

2. **Implement Business Logic**: In `plugin_name/__init__.py`, implement the business logic for your plugin. This could be anything from data processing to extended application functionalities.

3. **Define API Routes**: If your plugin exposes API endpoints, define these routes in `plugin_name/routes.py`. Use FastAPI's router to easily integrate with the main application.

#### Example: setup.py for Your Plugin

```python
from setuptools import setup, find_packages

setup(
    name='plugin_name',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        # Any other dependencies your plugin requires
    ],
    # Optionally define entry points for dynamic discovery if needed
)
```

#### Example: Plugin Business Logic and Routes

```python
# plugin_name/plugin_name/__init__.py
def process_data(data):
    # Business logic here
    return data

# plugin_name/plugin_name/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example_route():
    return {"message": "This route is provided by plugin_name."}
```

## API Documentation

  

FastAPI provides automatic interactive documentation at [http://localhost:8000/docs](http://localhost:8000/docs) or [http://localhost:8000/redoc](http://localhost:8000/redoc)

  
  

### Environment Variables

  

Create a `.env` at root with the following environment variables:

  
  

```ini

# .env

AUTH0_DOMAIN=

AUTH0_API_AUDIENCE=

AUTH0_ISSUER=

AUTH0_ALGORITHMS=

```

  

### Docker-Compose Commands

  

**Quick Start:** Run the following command to build the image, upgrade the database, and run the application. This will create the image that will be used to run the application, and run the application.

  

```bash

docker-compose  up  --build

```

  

**Build the image:** Run the following command to build the image. This will create the image that will be used to run the application.

  

```bash

docker-compose  build

```

  

```bash

docker-compose  up

```

  

### DockerFile Commands

  

Create the folders that will be mounted to the container.

  

**Windows:**

  

```bash

# building the image

docker  build  -t  fastapi_boilerplate:latest  .

# run the image, pass the environment variables, and mount the db & logs directories

docker  run  --env-file  .\.env  -p  8000:8000  -v ${PWD}/logs:/code/logs  fastapi_boilerplate:latest

```

  

**Mac/Linux:**

  

```bash

# building the image

docker  build  -t  fastapi_boilerplate:latest  .

# run the image, pass the environment variables, and mount the db & logs directories

docker  run  --env-file  .env  -p  8000:8000  -v  $(pwd)/logs:/code/logs  fastapi_boilerplate:latest

```

  

## Directory Structure

  

```mint

.

├── app/ # Main FastAPI application

├── appfrwk/ # Common framework code

├── .env # Env vars must be created and set here

├── docker-compose.yml # Pulls carlomos/firehoseai-api:latest

├── requirements.txt # Python dependencies

└── setup.py # Python package setup