from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..dependencies.mongodb import Mongodb
from ..dependencies.templates import templates


router = APIRouter()


@router.post('/search')
async def search_query(request: Request, bookid: str = Form(...)):
    return RedirectResponse(url='/books/{}'.format(bookid), status_code=303)


@router.get('/', response_class=HTMLResponse)
async def get_books(request: Request, mongodb: Mongodb = Depends(Mongodb)):
    books = mongodb.read_books()
    return templates.TemplateResponse(
        'index.html',
        {'request': request, 'title': 'home', 'books': books}
    )
