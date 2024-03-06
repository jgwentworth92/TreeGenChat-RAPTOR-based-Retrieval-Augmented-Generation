# FastApiJWTReader

## Description

FastApiJWTReader offers a secure, scalable solution for JWT token authentication and management within FastAPI applications. Utilizing Auth0, it ensures robust security measures are in place, simplifying the authentication process while maintaining high security standards.

## Plugin System Overview

This project implements a dynamic plugin system, designed to delegate business logic and application functionalities into separate, interchangeable modules known as "plugins". This system allows for easy extension and customization of the application by adding or removing plugins without altering the core application code.

### How It Works

The application automatically discovers and loads plugins located in the `appfrwk/plugins` directory. Each plugin is a Python module or package that adheres to a specific structure, namely implementing a base `Plugin` class. The `PluginManager` handles the loading, listing, and execution of these plugins, enabling the application to execute plugin-specific logic dynamically based on incoming requests.

### Creating a Plugin

To create a new plugin, follow these steps:

1. Place your plugin within the `appfrwk/plugins` directory.
2. Your plugin should include an `__init__.py` file that defines a class inheriting from the `Plugin` base class.
3. Implement the `execute` method in your plugin class, which will contain the business logic for that plugin.

#### Plugin Structure Example

```python
# appfrwk/plugins/example_plugin/__init__.py

from appfrwk.plugins.plugin_base import Plugin

class ExamplePlugin(Plugin):
    def __init__(self):
        super().__init__("ExamplePlugin")

    def execute(self, data):
        # Plugin-specific business logic here
        return {"message": "This is an example plugin execution", "input": data}
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
docker-compose up --build
```

**Build the image:** Run the following command to build the image. This will create the image that will be used to run the application.

```bash
docker-compose build
```

```bash
docker-compose up
```

### DockerFile Commands

Create the folders that will be mounted to the container.

**Windows:**

```bash
# building the image
docker build -t fastapi_boilerplate:latest .
# run the image, pass the environment variables, and mount the db & logs directories
docker run --env-file .\.env -p 8000:8000 -v ${PWD}/logs:/code/logs fastapi_boilerplate:latest
```

**Mac/Linux:** I think

```bash
# building the image
docker build -t fastapi_boilerplate:latest .
# run the image, pass the environment variables, and mount the db & logs directories
docker run --env-file .env -p 8000:8000  -v $(pwd)/logs:/code/logs fastapi_boilerplate:latest
```

## Directory Structure

```mint
.
├── app/                # Main FastAPI application
├── appfrwk/            # Common framework code
├── .env                # Env vars must be created and set here
├── docker-compose.yml  # Pulls carlomos/firehoseai-api:latest
├── requirements.txt    # Python dependencies
└── setup.py            # Python package setup