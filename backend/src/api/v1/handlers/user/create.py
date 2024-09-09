from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from backend.src.utils.providers.stub import Stub
from backend.src.database.gateway import DBGateway
from backend.src.common.dto.user import UserSchema, UserResponseSchema
from backend.src.services.security.bcrypt_hasher import BcryptHasher
from backend.src.common.converters.database import from_model_to_dto
from backend.src.common.exceptions import ConflictException


class CreateUserHandler:
    def __init__(
            self,
            gateway: Annotated[DBGateway, Depends(Stub(DBGateway))],
            hasher: Annotated[BcryptHasher, Depends(Stub(BcryptHasher))]
    ) -> None:
        self._gateway = gateway
        self._hasher = hasher

    async def execute(self, query: UserSchema) -> UserResponseSchema:
        query.password = self._hasher.hash_password(query.password)

        async with self._gateway:
            try:
                await self._gateway.manager.create_transaction()
                result = await self._gateway.user().create(**query.model_dump())

                return from_model_to_dto(result, UserResponseSchema)

            except IntegrityError:
                raise ConflictException('This user already exists')