from fastapi import FastAPI
import uvicorn

from .routers import assets, books, itunes_api, content_metadata


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
    title='Booktracker REST API',
    description='Books, tracked',
    openapi_tags=tags_metadata,
)

app.include_router(assets.router)
app.include_router(books.router)
app.include_router(itunes_api.router)
app.include_router(content_metadata.router)


def main():
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level='info')


if __name__ == '__main__':
    main()
