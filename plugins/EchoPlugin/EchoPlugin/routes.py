from fastapi import APIRouter

router = APIRouter()

@router.post("/echo")
async def echo(message: str):
    return {"message": message}

def add_routes(app):
    app.include_router(router)
