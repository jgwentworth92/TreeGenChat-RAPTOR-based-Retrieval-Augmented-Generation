from pydantic import BaseModel

class UserBase(BaseModel):
    """
    Users base schema
    """
    sub: str

class UserCreate(UserBase):
    """
    Users creation schema
    """
    pass