from typing import Optional
from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    aud: str
    iat: int
    exp: int
    iss: str
    scope: Optional[str] = None

class TokenVerificationResult(BaseModel):
    verified: bool
    payload: Optional[TokenPayload]
    sub: Optional[str] = None