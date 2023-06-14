import datetime
from typing import Any, List

from fastapi import Depends, HTTPException, UploadFile
from pydantic import BaseModel

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


class GetAdData(AdData):
    media: list[str]


class CreateAdResponse(AppModel):
    id: str


class DeleteAdMedia(BaseModel):
    media: list[str]


class Comment(BaseModel):
    _id: str
    content: str
    created_at: datetime.datetime
    author_id: str


@router.post("/", response_model=CreateAdResponse)
def create_ad(
    ad_data: AdData,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> dict[str, Any]:
    ad_id = svc.repository.create_ad(ad_data.dict(), jwt_data.user_id)
    return {"id": str(ad_id)}


@router.get("/{ad_id}", response_model=GetAdData)
def get_ad(
    ad_id: str,
    svc: Service = Depends(get_service),
) -> dict[str, Any]:
    ad = svc.repository.get_ad_by_id(ad_id)
    print(ad)
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


@router.post("/{ad_id}")
def upload_files(
    ad_id: str,
    files: List[UploadFile],
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> None:
    """
    file.filename: str - Название файла
    file.file: BytesIO - Содержимое файла
    """
    ad = svc.repository.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    result = []
    for file in files:
        url = svc.s3_service.upload_file(file.file, f"{ad_id}/{file.filename}")
        result.append(url)

    svc.repository.post_media(ad_id, result)


@router.delete("/{ad_id}/media")
def delete_ad_media(
    ad_id: str,
    media: DeleteAdMedia,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    ad = svc.repository.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    for filename in media.dict()["media"]:
        svc.s3_service.delete_file(filename)

    svc.repository.delete_media(ad_id)


@router.post("/{ad_id}/comments")
def add_comment(
    ad_id: str,
    comment_content: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> None:
    svc.repository.add_comment(ad_id, comment_content, jwt_data.user_id)


@router.get("/{ad_id}/comments", response_model=Any)
def get_comments(
    ad_id: str,
    svc: Service = Depends(get_service),
) -> dict[str, Any]:
    comments = svc.repository.get_comments_by_ad_id(ad_id)
    if not comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    print(comments)
    return {"comments": comments}


@router.patch("/{ad_id}/comments/{comment_id}")
def update_comment(
    ad_id: str,
    comment_id: str,
    comment_content: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> None:
    svc.repository.update_comment(ad_id, comment_id, comment_content, jwt_data.user_id)


@router.delete("/{ad_id}/comments/{comment_id}")
def delete_comment(
    ad_id: str,
    comment_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> None:
    svc.repository.delete_comment(ad_id, comment_id, jwt_data.user_id)
