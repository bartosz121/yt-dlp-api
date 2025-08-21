from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

from yt_dlp_api.config import settings


class AuthenticationMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:  # pyright: ignore[reportUnknownParameterType, reportMissingTypeArgument]
        auth_header = connection.headers.get("authorization")
        if not auth_header:
            raise HTTPException(status_code=403, detail="")

        if auth_header != settings.AUTHORIZATION_SECRET:
            raise HTTPException(status_code=403, detail="")

        return AuthenticationResult(user="admin", auth={})
