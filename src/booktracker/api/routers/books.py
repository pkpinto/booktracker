from aiohttp.client_exceptions import ClientConnectorError
from fastapi import APIRouter, Depends

from ..dependencies.mongodb import Asset, Book
from . import assets, content_metadata


router = APIRouter(prefix='/books', tags=['Books'])


@router.get('/')
async def get_books(book_db: Book = Depends(Book)):
    return list(book_db.get_books())


@router.get('/{bookid}')
async def book_detail(bookid: str, book_db: Book = Depends(Book)):

    try:
        book = next(book_db.get_books(bookid))
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
async def upsert_book_asset(bookid: str, db: Asset = Depends(Asset)):

    book_data = await content_metadata.get_asset(assetid=bookid)
    asset_r = await assets.upsert_asset(assetid=bookid, data=book_data, db=db)

    artwork = await content_metadata.get_asset_artwork(assetid=bookid, stream_output=False)
    asset_artwork_r = await assets.upsert_asset_artwork(assetid=bookid, file=artwork, db=db)

    return {'asset': asset_r, 'asset_artwork': asset_artwork_r}


@router.delete('/{bookid}', summary='Delete assets underlying book')
async def delete_book_asset(bookid: str, db: Asset = Depends(Asset)):

    asset_r = await assets.delete_asset(assetid=bookid, db=db)
    asset_artwork_r = await assets.delete_asset_artwork(assetid=bookid, db=db)

    return {'asset': asset_r, 'asset_artwork': asset_artwork_r}
