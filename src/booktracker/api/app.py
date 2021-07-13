from fastapi import FastAPI
import uvicorn

from .routers import assets, books, content_metadata


app = FastAPI(
    title='Booktracker REST API',
    description='Track books in collection',
)

app.include_router(assets.router)
app.include_router(books.router)
app.include_router(content_metadata.router)


@app.get('/', summary='List routes')
async def get_assets():
    return [
        assets.router.prefix.strip('/'),
        books.router.prefix.strip('/'),
        content_metadata.router.prefix.strip('/'),
    ]


def main():
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level='info')


if __name__ == '__main__':
    main()
