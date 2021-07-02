import io
from typing import Dict

from fastapi import APIRouter, Depends, File
from fastapi.responses import StreamingResponse

from ..dependencies.mongodb import Mongodb


router = APIRouter(prefix='/local-assets', tags=['Local asset data'])


@router.get('/', summary='List locally stored assets')
async def get_assets(mongodb: Mongodb = Depends(Mongodb)):
    return mongodb.list_assets()


@router.get('/{assetid}', summary='Asset details')
async def get_asset(assetid: str, mongodb: Mongodb = Depends(Mongodb)):
    return mongodb.read_asset(assetid=assetid)


@router.put('/{assetid}', summary='Insert asset into local store')
@router.patch('/{assetid}', summary='Update asset in local store')
async def upsert_asset(assetid: str, asset: Dict, mongodb: Mongodb = Depends(Mongodb)):
    return mongodb.upsert_asset(assetid=assetid, data=asset)


@router.delete('/{assetid}', summary='Delete asset from local store')
async def delete_asset(assetid: str, mongodb: Mongodb = Depends(Mongodb)):
    return mongodb.delete_asset(assetid=assetid)


@router.get('/{assetid}/artwork', summary='Asset artwork', response_class=StreamingResponse)
async def get_asset_artwork(assetid: str, mongodb: Mongodb = Depends(Mongodb)):
    artwork = mongodb.read_asset_artwork(assetid=assetid)
    return StreamingResponse(io.BytesIO(artwork), media_type='image/jpeg')


@router.put('/{assetid}/artwork', summary='Insert asset artwork into local store')
@router.patch('/{assetid}/artwork', summary='Update asset artwork in local store')
async def upsert_asset_artwork(assetid: str, file: bytes = File(...), mongodb: Mongodb = Depends(Mongodb)):
    # using file: bytes (not UploadFile) so we can call this function with a bytes object
    artwork = io.BytesIO(file)
    return mongodb.upsert_asset_artwork(assetid=assetid, data=artwork.getvalue())


@router.delete('/{assetid}/artwork', summary='Delete asset artwork from local store')
async def delete_asset_artwork(assetid: str, mongodb: Mongodb = Depends(Mongodb)):
    return mongodb.delete_asset_artwork(assetid=assetid)
