from app.config import get_config
from fastapi import FastAPI
from app.routers import rag, oauth  # Make sure these imports match your project structure.
from app.utils.common import setup_logging

# This function sets up logging based on the configuration specified in your logging configuration file.
# It's important for monitoring and debugging.
setup_logging()

# This ensures that the directory for storing QR codes exists when the application starts.
# If it doesn't exist, it will be created.


# This creates an instance of the FastAPI application.
app = FastAPI(
    title="QR Code Manager",
    description="A FastAPI application for creating, listing available codes, and deleting QR codes. "
                "It also supports OAuth for secure access.",
    version="0.0.1",
        redoc_url=None,
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }

)

# Here, we include the routers for our application. Routers define the paths and operations your API provides.
# We have two routers in this case: one for managing QR codes and another for handling OAuth authentication.
config = get_config()
app.include_router(oauth.router)  # OAuth authentication routes
app.include_router(rag.router)  