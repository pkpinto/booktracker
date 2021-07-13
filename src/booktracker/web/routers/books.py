import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..dependencies.templates import templates


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
async def get_books(request: Request):

    url = 'http://localhost:5000/books'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            books = await response.json()

    artwork_url_template = 'http://localhost:5000/assets/{asset_id}/artwork'
    for book in books:
        book['artwork'] = artwork_url_template.format(asset_id=book['_id'])

    return templates.TemplateResponse(
        'books.html',
        {'request': request, 'title': 'books', 'books': books}
    )


@router.get('/{bookid}', response_class=HTMLResponse)
async def book_detail(request: Request, bookid: str):

    url = 'http://localhost:5000/books/{bookid}'.format(bookid=bookid)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            r = await response.json()

    # except ClientConnectorError:
    #     raise HTTPException(status_code=404,
    #                         detail='No local content and cannot connect to content metadata server')

    # raise HTTPException(status_code=404,
    #                     detail='No local content and assetid {} not found in content metadata server'.format(bookid))

    data_source = r['data_source']
    book = r['books'][0]
    book['description']['standard'] = Markup(book['description']['standard'])

    artwork_url_template = 'http://localhost:5000/{data_source}/{asset_id}/artwork'
    book['artwork'] = artwork_url_template.format(data_source=data_source, asset_id=book['_id'])

    return templates.TemplateResponse(
        'book_detail.html',
        {'request': request, 'title': bookid, 'book': book, 'data_source': data_source}
    )


@router.put('/{bookid}', summary='Insert assets underlying book')
@router.patch('/{bookid}', summary='Update assets underlying book')
async def upsert_book_asset(bookid: str):

    url = 'http://localhost:5000/books/{bookid}'.format(bookid=bookid)
    async with aiohttp.ClientSession() as session:
        async with session.put(url) as response:
            return await response.json()


@router.delete('/{bookid}', summary='Delete assets underlying book')
async def delete_book_asset(bookid: str):

    url = 'http://localhost:5000/books/{bookid}'.format(bookid=bookid)
    async with aiohttp.ClientSession() as session:
        async with session.delete(url) as response:
            return await response.json()
