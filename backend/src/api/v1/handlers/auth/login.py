from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.src.utils.providers.stub import Stub
from backend.src.services.security.bcrypt_hasher import BcryptHasher
from backend.src.services.security.token_jwt import TokenJWT
from backend.src.database.gateway import DBGateway
from backend.src.common.exceptions import UnAuthorizedException
from backend.src.common.dto.token_jwt import Token, TokenSubject
from backend.src.common.dto.user import UserInDBSchema
from backend.src.common.exceptions import NotFoundException
from backend.src.common.converters.database import from_model_to_dto


class LoginHandler:
    def __init__(
            self,
            gateway: Annotated[DBGateway, Depends(Stub(DBGateway))],
            hasher: Annotated[BcryptHasher, Depends(Stub(BcryptHasher))],
            jwt: Annotated[TokenJWT, Depends(Stub(TokenJWT))]
    ) -> None:
        self._gateway = gateway
        self._hasher = hasher
        self._jwt = jwt

    async def execute(self, query: OAuth2PasswordRequestForm) -> Token:
        async with self._gateway:
            fetched_user = await self._gateway.user().get_one(login=query.username)

        if not fetched_user:
            raise NotFoundException('User not found')

        current_user = from_model_to_dto(fetched_user, UserInDBSchema)

        if not self._hasher.verify_password(query.password, current_user.password):
            raise UnAuthorizedException('Incorrect password')

        token_data = TokenSubject(sub=current_user.id, scopes=query.scopes)
        token = self._jwt.create_jwt_token(token_data.model_dump())

        return Token(access_token=token, token_type='Bearer')
