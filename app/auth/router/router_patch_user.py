from typing import Any

from fastapi import Depends
from pydantic import BaseModel, Field

from app.utils import AppModel

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router
from .dependencies import parse_jwt_user_data


class UserPatchModel(BaseModel):
    phone: str
    name: str
    city: str


class PatchMyAccountResponse(AppModel):
    pass


@router.patch("/users/me", response_model=PatchMyAccountResponse)
def patch_my_account(
    data: UserPatchModel,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, str]:
    svc.repository.update_user(jwt_data.user_id, data.dict())
    return data.dict()
