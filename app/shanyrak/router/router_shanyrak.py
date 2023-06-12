from typing import Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from app.utils import AppModel

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router
from .dependencies import parse_jwt_user_data


class AdData(BaseModel):
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str


class CreateAdResponse(AppModel):
    id: str


@router.post("/", response_model=CreateAdResponse)
def create_ad(
    ad_data: AdData,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, Any]:
    ad_id = svc.repository.create_ad(ad_data.dict(), jwt_data.user_id)
    return {"id": str(ad_id)}


@router.get("/{ad_id}", response_model=AdData)
def get_ad(
    ad_id: str,
    svc: Service = Depends(get_service),
) -> dict[str, Any]:
    ad = svc.repository.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


@router.patch("/{ad_id}")
def update_ad(
    ad_id: str,
    ad_data: AdData,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> None:
    svc.repository.update_ad(ad_id, ad_data.dict())


@router.delete("/{ad_id}")
def delete_ad(
    ad_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> None:
    svc.repository.delete_ad(ad_id)
