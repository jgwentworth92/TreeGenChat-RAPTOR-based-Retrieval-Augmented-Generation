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

class DocumentInput(BaseModel):
    pdf_filename: str
    max_iteration: int

class QuickMessage(BaseModel):
    question: str
