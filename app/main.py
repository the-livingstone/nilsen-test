from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, Response
from app.cache import Cache
from app.settings import AppSettings
from logging import getLogger, FileHandler, INFO
from pprint import pformat
from api.api import router
from app.settings import settings
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = Cache(capacity=settings.cache_size)
    app.state.cache = cache
    yield


def create_app(settings: AppSettings) -> FastAPI:
    app = FastAPI(
        title=settings.title,
        docs_url="/api/_docs",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app(settings)
log = getLogger(__name__)
log.setLevel(INFO)
file_handler = FileHandler('log/log.log')
file_handler.setLevel(INFO)
log.addHandler(file_handler)

@app.middleware('http')
async def logging(request: Request, call_next):
    log.info(f'{datetime.now()} {request.method} {request.url}')
    response: Response = await call_next(request)
    log.info(f'{datetime.now()} response: {response.status_code}')
    return response


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
