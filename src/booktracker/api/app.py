from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from .dependencies.mongodb import Mongodb, ServerSelectionTimeoutError
from .routers import assets, books, itunes_api, content_metadata
from ..config import config, Config


def create_app(config: Config = None) -> FastAPI:

    tags_metadata = [
        {
            'name': 'Apple Content Metadata',
            'externalDocs': {
                'description': 'External docs',
                'url': 'https://developer.apple.com/documentation/devicemanagement/app_and_book_management/getting_app_and_book_information',
            }
        },
        {
            'name': 'Apple iTunes API',
            'externalDocs': {
                'description': 'External docs',
                'url': 'https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api',
            },
        },
    ]

    app = FastAPI(
        title=config.api.title,
        description=config.api.description,
        openapi_tags=tags_metadata,
    )

    @app.on_event('startup')
    async def mongodb_startup() -> None:
        app.state.mongodb = Mongodb(
            host=config.api.mongodb.host,
            replicaset=config.api.mongodb.replicaset,
            database=config.api.mongodb.database,
        )

    @app.exception_handler(ServerSelectionTimeoutError)
    async def mongo_timeout_exception_handler(request, e):
        return JSONResponse(
            status_code=503,
            content={'details': str(e)},
        )

    app.include_router(assets.router, prefix='/assets')
    app.include_router(books.router, prefix='/books')
    app.include_router(content_metadata.router, prefix='/content-metadata')
    app.include_router(itunes_api.router, prefix='/itunes-api')

    return app


def main():
    app = create_app(config=config)
    uvicorn.run(app, host=config.api.host, port=config.api.port)


if __name__ == '__main__':
    main()
