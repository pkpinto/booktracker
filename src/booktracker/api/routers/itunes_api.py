import aiohttp
import asyncstdlib as a
from fastapi import APIRouter, HTTPException


router = APIRouter(prefix='/itunes-api', tags=['Apple iTunes API'])


@a.lru_cache
async def _query_itunes_api(assetid, store='GB'):

    url = 'https://itunes.apple.com/lookup?id={id}&country={store}'.format(id=assetid, store=store)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json(content_type=None)
    except aiohttp.ClientConnectionError:
        raise HTTPException(status_code=503, detail='Apple iTunes API not available')


@router.get('/{assetid}', summary='Asset details')
async def get_asset(assetid: str):
    return await _query_itunes_api(assetid=assetid)
