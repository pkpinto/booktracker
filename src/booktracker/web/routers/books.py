import aiohttp
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..dependencies.templates import templates
from ...config import config


router = APIRouter()


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

    url = '{backend_url}/books'.format(backend_url=config.web.backend_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            books = await response.json()

    artwork_url_template = '{backend_url}/assets/{asset_id}/artwork'
    for book in books:
        book['artwork'] = artwork_url_template.format(backend_url=config.web.backend_url, asset_id=book['_id'])

    return templates.TemplateResponse(
        'books.html',
        {'request': request, 'title': 'books', 'books': books}
    )


@router.get('/{bookid}', response_class=HTMLResponse)
async def book_detail(request: Request, bookid: str):

    url = '{backend_url}/books/{bookid}'.format(backend_url=config.web.backend_url, bookid=bookid)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise HTTPException(status_code=404, detail='No local content and Apple Content Metadata does not return data')
            if response.status == 503:
                raise HTTPException(status_code=404, detail='No local content and Apple Content Metadata is not available')
            r = await response.json()

    data_source = r['data_source']
    book = r['books'][0]
    book['description']['standard'] = Markup(book['description']['standard'])

    artwork_url_template = '{backend_url}/{data_source}/{asset_id}/artwork'
    book['artwork'] = artwork_url_template.format(backend_url=config.web.backend_url, data_source=data_source, asset_id=book['_id'])

    return templates.TemplateResponse(
        'book_detail.html',
        {'request': request, 'title': bookid, 'book': book, 'data_source': data_source}
    )


@router.put('/{bookid}', summary='Insert assets underlying book')
@router.patch('/{bookid}', summary='Update assets underlying book')
async def upsert_book_asset(bookid: str):

    url = '{backend_url}/books/{bookid}'.format(backend_url=config.web.backend_url, bookid=bookid)
    async with aiohttp.ClientSession() as session:
        async with session.put(url) as response:
            return await response.json()


@router.delete('/{bookid}', summary='Delete assets underlying book')
async def delete_book_asset(bookid: str):

    url = '{backend_url}/books/{bookid}'.format(backend_url=config.web.backend_url, bookid=bookid)
    async with aiohttp.ClientSession() as session:
        async with session.delete(url) as response:
            return await response.json()
