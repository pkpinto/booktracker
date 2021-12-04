from aiohttp.client_exceptions import ClientConnectorError
from fastapi import APIRouter, Depends
from starlette.requests import Request

# get_mongodb needs `request: Request` to be added to the function signature for dependency resolution
from ..dependencies.mongodb import get_mongodb, Mongodb
from . import assets, content_metadata


router = APIRouter(tags=['Books'])


@router.get('/')
async def get_books(request: Request, db: Mongodb = Depends(get_mongodb)):
    return list(db.get_books())


@router.get('/{bookid}')
async def book_detail(bookid: str, request: Request, db: Mongodb = Depends(get_mongodb)):

    try:
        book = next(db.get_books(bookid))
        return {'data_source': 'assets', 'books': [book]}

    except StopIteration:

        try:
            cm = await content_metadata.get_asset(bookid)
        except ClientConnectorError:
            return {'data_source': 'assets', 'books': []}

        try:
            b = cm['results'][bookid]
            book = {
                '_id': bookid,
                'name': b['name'],
                'nameSortValue': b['nameSortValue'],
                'artistName': b['artistName'],
                'artistId': b['artistId'],
                'releaseDate': b['releaseDate'],
            }
            book['ebookInfo'] = {
                'publisher': b['ebookInfo'].get('publisher'),
                'subtitle': b['ebookInfo'].get('subtitle'),
                'seriesInfo': b['ebookInfo'].get('seriesInfo'),
                'sequenceNumber': b['ebookInfo'].get('sequenceNumber'),
            }
            book['description'] = {
                'standard': b['description']['standard'],
            }
        except KeyError:
            return {'data_source': 'content-metadata', 'books': []}

        return {'data_source': 'content-metadata', 'books': [book]}


@router.put('/{bookid}', summary='Insert assets underlying book')
@router.patch('/{bookid}', summary='Update assets underlying book')
async def upsert_book_asset(bookid: str, request: Request, db: Mongodb = Depends(get_mongodb)):

    book_data = await content_metadata.get_asset(assetid=bookid)
    asset_r = await assets.upsert_asset(assetid=bookid, data=book_data, request=request, db=db)

    artwork = await content_metadata.get_asset_artwork(assetid=bookid, stream_output=False)
    asset_artwork_r = await assets.upsert_asset_artwork(assetid=bookid, file=artwork, request=request, db=db)

    return {'asset': asset_r, 'asset_artwork': asset_artwork_r}


@router.delete('/{bookid}', summary='Delete assets underlying book')
async def delete_book_asset(bookid: str, request: Request, db: Mongodb = Depends(get_mongodb)):

    asset_r = await assets.delete_asset(assetid=bookid, db=db)
    asset_artwork_r = await assets.delete_asset_artwork(assetid=bookid, db=db)

    return {'asset': asset_r, 'asset_artwork': asset_artwork_r}
