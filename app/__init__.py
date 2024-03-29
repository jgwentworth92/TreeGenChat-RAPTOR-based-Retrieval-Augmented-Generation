from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.plugin import load_plugins
from app.api.router.routes import router
from appfrwk.config import get_config
from appfrwk.logging_config import setup_logging, get_logger
from appfrwk.logging_config.log_middleware import LogMiddleware
from appfrwk.utils.verify_token import VerifyToken

# Setup logging configuration
setup_logging()


def create_app():
    """
    Create a FastAPI application
    """

    # Fetch configurations from the environment
    config = get_config()

    # Create FastAPI app instance with provided configurations
    app = FastAPI(
        title=config.TITLE,
        description=config.DESCRIPTION,
        version=config.VERSION,
        debug=config.DEBUG,
        testing=config.TESTING
    )

    # Add middleware
    app.add_middleware(LogMiddleware)
    app.include_router(router)
    # Include routers. Now, we're using a more generalized import from the 'routers' folder

    # Root endpoint
    @app.get("/")
    async def root():
        """
        Root endpoint
        """
        logger = get_logger(config.APP_NAME)
        logger.info("Root endpoint accessed")
        return {"message": "Hello World"}

    return app
