from typing import Optional, Any
from datetime import datetime, timedelta

import jwt

from user_service.src.core.settings import JWTSettings
from user_service.src.common.exceptions import InvalidTokenException


class TokenJWT:
    def __init__(self, settings: JWTSettings) -> None:
        self.settings = settings

    def create_jwt_token(self, data: dict) -> str:
        expiration = datetime.utcnow() + timedelta(minutes=self.settings.jwt_expiration)
        data.update({"exp": expiration})
        token = jwt.encode(data, self.settings.private_key, algorithm=self.settings.algorithm)
        return token

    def verify_jwt_token(self, token: str) -> Optional[Any]:
        try:
            decoded_data = jwt.decode(
                token,
                self.settings.public_key,
                algorithms=[self.settings.algorithm]
            )
            return decoded_data

        except jwt.PyJWTError:
            raise InvalidTokenException('Token is invalid or expired')
