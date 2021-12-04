import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn

from .dependencies.templates import templates
from .routers import books, root
from ..config import config, Config


def create_app(config: Config = None) -> FastAPI:

    app = FastAPI(
        title=config.web.title,
        description=config.web.description,
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, e):
        return templates.TemplateResponse('404.html', {'request': request, 'detail': e.detail}, status_code=404)

    static_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    app.mount('/static', StaticFiles(directory=static_folder), name='static')

    app.include_router(root.router)
    app.include_router(books.router, prefix='/books')

    return app


def main():
    app = create_app(config=config)
    uvicorn.run(app, host=config.web.host, port=config.web.port)


if __name__ == '__main__':
    main()
