import io
from typing import Dict

from fastapi import APIRouter, Depends, File
from fastapi.responses import StreamingResponse
from starlette.requests import Request

# get_mongodb needs `request: Request` to be added to the function signature for dependency resolution
from ..dependencies.mongodb import get_mongodb, Mongodb


router = APIRouter(tags=['Local asset data'])


@router.get('/', summary='List locally stored assets')
async def get_assets(request: Request, db: Mongodb = Depends(get_mongodb)):
    return db.list_assets()


@router.get('/{assetid}', summary='Asset details')
async def get_asset(assetid: str, request: Request, db: Mongodb = Depends(get_mongodb)):
    return db.get_asset(assetid=assetid)


@router.put('/{assetid}', summary='Insert asset into local store')
@router.patch('/{assetid}', summary='Update asset in local store')
async def upsert_asset(assetid: str, data: Dict, request: Request, db: Mongodb = Depends(get_mongodb)):
    return db.upsert_asset(assetid=assetid, data=data)


@router.delete('/{assetid}', summary='Delete asset from local store')
async def delete_asset(assetid: str, request: Request, db: Mongodb = Depends(get_mongodb)):
    return db.delete_asset(assetid=assetid)


@router.get('/{assetid}/artwork', summary='Asset artwork', response_class=StreamingResponse)
async def get_asset_artwork(assetid: str, request: Request, db: Mongodb = Depends(get_mongodb)):
    artwork = db.get_asset_artwork(assetid=assetid)
    return StreamingResponse(io.BytesIO(artwork), media_type='image/jpeg')


@router.put('/{assetid}/artwork', summary='Insert asset artwork into local store')
@router.patch('/{assetid}/artwork', summary='Update asset artwork in local store')
async def upsert_asset_artwork(assetid: str, request: Request, file: bytes = File(...), db: Mongodb = Depends(get_mongodb)):
    # using file: bytes (not UploadFile) so we can call this function with a bytes object
    artwork = io.BytesIO(file)
    return db.upsert_asset_artwork(assetid=assetid, data=artwork.getvalue())


@router.delete('/{assetid}/artwork', summary='Delete asset artwork from local store')
async def delete_asset_artwork(assetid: str, request: Request, db: Mongodb = Depends(get_mongodb)):
    return db.delete_asset_artwork(assetid=assetid)
