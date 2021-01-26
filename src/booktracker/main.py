from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dependencies.mongodb import Mongodb
from routers import books, content_metadata, local_assets


app = FastAPI(
    title='Booktracker',
    description='Track books in collection'
)

app.mount('/static', StaticFiles(directory='static'), name='static')
app.include_router(books.router)
app.include_router(local_assets.router)
app.include_router(content_metadata.router)

templates = Jinja2Templates(directory='templates')

@app.exception_handler(HTTPException)
async def http_exception_handler(request, e):
    return templates.TemplateResponse('404.html', {'request': request, 'detail': e.detail}, status_code=404)

@app.post('/search')
async def search_query(request: Request, bookid: str = Form(...)):
    return RedirectResponse(url='/books/{}'.format(bookid), status_code=303)

@app.get('/', response_class=HTMLResponse)
async def get_books(request: Request, mongodb: Mongodb = Depends(Mongodb)):
    books = mongodb.read_books()
    return templates.TemplateResponse(
        'index.html',
        {'request': request, 'title': 'home', 'books': books}
    )
