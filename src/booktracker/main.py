import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn

from .dependencies.templates import templates
from .routers import books, content_metadata, local_assets, root


app = FastAPI(
    title='Booktracker',
    description='Track books in collection'
)

static_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
app.mount('/static', StaticFiles(directory=static_folder), name='static')

app.include_router(root.router)
app.include_router(books.router)
app.include_router(local_assets.router)
app.include_router(content_metadata.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, e):
    return templates.TemplateResponse('404.html', {'request': request, 'detail': e.detail}, status_code=404)


def main():
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level='info')


if __name__ == '__main__':
    main()
