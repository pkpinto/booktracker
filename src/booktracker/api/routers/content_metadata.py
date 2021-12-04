import io

import aiohttp
from asyncstdlib import lru_cache
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(tags=['Apple Content Metadata'])


# @lru_cache
async def _query_content_metadata(assetid, store='gb'):

    url = 'https://uclient-api.itunes.apple.com/WebObjects/MZStorePlatform.woa/wa/lookup?version=2&id={id}&p=mdm-lockup&caller=MDM&platform=omni&cc={store}'.format(id=assetid, store=store)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    raise HTTPException(status_code=404, detail='Apple Content Metadata does not return data')
                return await response.json()
    except aiohttp.ClientConnectionError:
        raise HTTPException(status_code=503, detail='Apple Content Metadata is not available')


@router.get('/{assetid}', summary='Asset details')
async def get_asset(assetid: str):
    return await _query_content_metadata(assetid=assetid)


@lru_cache
@router.get('/{assetid}/artwork', summary='Asset artwork', response_class=StreamingResponse)
async def get_asset_artwork(assetid: str, stream_output: bool = True):

    content_metadata = await _query_content_metadata(assetid=assetid)
    if content_metadata['results'].get(assetid, False):

        url = content_metadata['results'][assetid]['artwork']['url'].format(
            w=content_metadata['results'][assetid]['artwork']['width'],
            h=content_metadata['results'][assetid]['artwork']['height'],
            f='jpg',
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    content = await response.content.read()
        except aiohttp.ClientConnectionError:
            raise HTTPException(status_code=503, detail='Apple Content Metadata not available')

        return StreamingResponse(io.BytesIO(content), media_type='image/jpeg') if stream_output else content

    else:
        return StreamingResponse(io.BytesIO(b'')) if stream_output else b''
