import aiohttp
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..dependencies.templates import templates
from ...config import config


router = APIRouter()


@router.post('/search')
async def search_query(request: Request, bookid: str = Form(...)):
    return RedirectResponse(url='/books/{}'.format(bookid), status_code=303)


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
        'index.html',
        {'request': request, 'title': 'home', 'books': books}
    )
