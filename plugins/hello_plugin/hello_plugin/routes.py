from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    return {"message": "Hello from the Hello Plugin!"}

def add_routes(app):
    app.include_router(router)
