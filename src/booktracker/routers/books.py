from aiohttp.client_exceptions import ClientConnectorError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..dependencies.mongodb import Mongodb
from ..dependencies.templates import templates
from . import content_metadata, local_assets


router = APIRouter(prefix='/books')


class Markup(str):
    '''
    Minimal implementation of the __html__ function that a couple of frameworks and web applications use
    for marking a string as being safe for inclusion in HTML/XML output without needing to be escaped.
    https://flask.palletsprojects.com/en/1.1.x/api/#flask.Markup
    '''
    def __html__(self):
        return self


@router.get('/', response_class=HTMLResponse)
async def get_books(request: Request, mongodb: Mongodb = Depends(Mongodb)):
    books = mongodb.read_books()
    return templates.TemplateResponse(
        'books.html',
        {'request': request, 'title': 'books', 'books': books}
    )


@router.get('/{bookid}', response_class=HTMLResponse)
async def book_detail(request: Request, bookid: str, mongodb: Mongodb = Depends(Mongodb)):

    try:
        book = mongodb.read_books(bookid)[0]
        data_source = 'local-assets'
    except IndexError:

        try:
            cm = await content_metadata.get_asset(bookid)
        except ClientConnectorError:
            raise HTTPException(status_code=404,
                                detail='No local content and cannot connect to content metadata server')

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
            data_source = 'content-metadata'
        except KeyError:
            raise HTTPException(status_code=404,
                                detail='No local content and assetid {} not found in content metadata server'.format(bookid))

    book['description']['standard'] = Markup(book['description']['standard'])

    return templates.TemplateResponse(
        'book_detail.html',
        {'request': request, 'title': bookid, 'book': book, 'data_source': data_source}
    )


@router.put('/{bookid}', summary='Insert assets underlying book')
@router.patch('/{bookid}', summary='Update assets underlying book')
# async def upsert_book_asset(bookid: str, book_data: Dict = Body(...), mongodb: Mongodb = Depends(Mongodb)):
async def upsert_book_asset(bookid: str, mongodb: Mongodb = Depends(Mongodb)):

    book_data = await content_metadata.get_asset(assetid=bookid)
    asset_r = await local_assets.upsert_asset(assetid=bookid, asset=book_data, mongodb=mongodb)

    artwork = await content_metadata.get_asset_artwork(assetid=bookid, stream_output=False)
    asset_artwork_r = await local_assets.upsert_asset_artwork(assetid=bookid, file=artwork, mongodb=mongodb)

    return {'asset': asset_r, 'asset_artwork': asset_artwork_r}


@router.delete('/{bookid}', summary='Delete assets underlying book')
async def delete_book_asset(bookid: str, mongodb: Mongodb = Depends(Mongodb)):

    asset_r = await local_assets.delete_asset(assetid=bookid, mongodb=mongodb)
    asset_artwork_r = await local_assets.delete_asset_artwork(assetid=bookid, mongodb=mongodb)

    return {'asset': asset_r, 'asset_artwork': asset_artwork_r}
