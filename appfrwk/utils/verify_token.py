import jwt
from jwt.exceptions import PyJWKClientError, DecodeError
from typing import Optional
from fastapi import Depends
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from fastapi import HTTPException, status
from appfrwk.errors import UnauthorizedException, UnauthenticatedException
from appfrwk.config import get_config
from app.api.schemas.token_schemas import TokenVerificationResult, TokenPayload
from appfrwk.logging_config import get_logger

log = get_logger(__name__)


class VerifyToken():
    def __init__(self):
        self.config = get_config()
        jwks_url = f'https://{self.config.AUTH0_DOMAIN}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)
        self.audience = self.config.AUTH0_API_AUDIENCE

    async def __call__(self, security_scopes: SecurityScopes,
                       token: Optional[HTTPAuthorizationCredentials] = Depends(
                           HTTPBearer())
                       ) -> TokenVerificationResult:
        if token is None:
            log.error("No token provided")
            raise UnauthenticatedException

        token = token.credentials
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token, signing_key, algorithms=self.config.AUTH0_ALGORITHMS, audience=self.config.AUTH0_API_AUDIENCE)
            return TokenVerificationResult(verified=True, payload=TokenPayload(**payload), sub=payload.get("sub"))
        except (PyJWKClientError, DecodeError, jwt.ExpiredSignatureError, Exception) as e:
            log.error(f"Token verification error: {str(e)}")
            raise UnauthorizedException(str(e))