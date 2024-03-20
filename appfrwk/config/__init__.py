"""FastAPI Configuration File"""
import os
import pathlib
from typing import List, Tuple, Union, Dict
# from appfrwk.config.agents_conf import AgentsConfig
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    """Base Configuration Class"""

    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # App Details
    APP_NAME: str = "FastAPI_Boilerplate"
    TITLE: str = "Fast API Boilerplate"
    DESCRIPTION: str = "Generalized fast api boilerplate with config and logging.."
    VERSION: str = "0.1.0"

    # Auth0 Config
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    AUTH0_ISSUER: str
    AUTH0_ALGORITHMS: str

    # Debug config
    DEBUG: bool = False
    TESTING: bool = False

    # Directory config
    APP_ROOT_DIRECTORY: str = os.getcwd()
    LOG_DIRECTORY: str = os.path.join(APP_ROOT_DIRECTORY, "logs")
    PLUGINS_DIRECTORY: str = os.path.join("appfrwk.plugins")  
    OPENAI_API_KEY: str
    SERVICE_MODEL: str = os.getenv("SERVICE_MODEL", "gpt-4")
    SERVICE_TEMPERATURE: float = os.getenv("SERVICE_TEMPERATURE", 0.5)
    SERVICE_MAX_TOKENS: int = os.getenv("SERVICE_MAX_TOKENS", 1000)
    SERVICE_FREQUENCY_PENALTY: float = os.getenv(
        "SERVICE_FREQUENCY_PENALTY", 0.5)
    SERVICE_PRESENCE_PENALTY: float = os.getenv("SERVICE_PRESENCE_PENALTY", 0)
    # Database config
    DATABASE_URL: str
    DATABASE_URL2:str
class ProductionConfig(Settings):
    pass


class DevelopmentConfig(Settings):
    model_config = SettingsConfigDict(env_file=os.path.join(
        os.getcwd(), '.env'), env_file_encoding='utf-8')
    DEBUG: bool = True


class TestingConfig(Settings):
    TESTING: bool = True
    DEBUG: bool = True


@lru_cache()
def get_config() -> Settings:
    """Get the current configuration object"""
    environment = os.getenv("ENVIRONMENT", "development")
    config = None
    if environment == "development":
        config = DevelopmentConfig()
    elif environment == "testing":
        config = TestingConfig()
    elif environment == "production":
        config = ProductionConfig()
    else:
        raise ValueError(f"Invalid environment: {environment}")

    return config
