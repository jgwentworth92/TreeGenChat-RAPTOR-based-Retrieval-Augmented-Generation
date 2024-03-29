from app import create_app
from appfrwk.config import get_config
import uvicorn

config = get_config()
app = create_app()
if __name__ == "__main__":
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)