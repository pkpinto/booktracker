import io

import aiohttp
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix='/content-metadata', tags=['Apple Content Metadata'])


async def _query_content_metadata(assetid, store='gb'):
    url = 'https://uclient-api.itunes.apple.com/WebObjects/MZStorePlatform.woa/wa/lookup?version=2&id={}&p=mdm-lockup&caller=MDM&platform=omni&cc={}'.format(assetid, store)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content_metadata = await response.json()
    content_metadata['_id'] = assetid
    return content_metadata


@router.get('/{assetid}', summary='Asset details')
async def get_asset(assetid: str):
    return await _query_content_metadata(assetid=assetid)


@router.get('/{assetid}/artwork', summary='Asset artwork', response_class=StreamingResponse)
async def get_asset_artwork(assetid: str, stream_output: bool = True):
    content_metadata = await _query_content_metadata(assetid=assetid)

    if content_metadata['results'].get(assetid, False):
        artwork_url = content_metadata['results'][assetid]['artwork']['url'].format(
            w=content_metadata['results'][assetid]['artwork']['width'],
            h=content_metadata['results'][assetid]['artwork']['height'],
            f='jpg',
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(artwork_url) as response:
                content = await response.content.read()
        return StreamingResponse(io.BytesIO(content), media_type='image/jpeg') if stream_output else content
    else:
        return StreamingResponse(io.BytesIO(b'')) if stream_output else b''
