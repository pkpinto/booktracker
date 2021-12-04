import aiohttp
from asyncstdlib import lru_cache
from fastapi import APIRouter, HTTPException


router = APIRouter(tags=['Apple iTunes API'])


@lru_cache
async def _query_itunes_api(assetid, store='GB'):

    url = 'https://itunes.apple.com/lookup?id={id}&country={store}'.format(id=assetid, store=store)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                r = await response.json(content_type=None)
                if 'resultCount' not in r.keys():
                    raise HTTPException(status_code=404, detail='Apple iTunes API does not return data')
                return r
    except aiohttp.ClientConnectionError:
        raise HTTPException(status_code=503, detail='Apple iTunes API is not available')


@router.get('/{assetid}', summary='Asset details')
async def get_asset(assetid: str):
    return await _query_itunes_api(assetid=assetid)
