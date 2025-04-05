from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.cache import Cache
from app.schemas import Intake

router = APIRouter(prefix='/cache')

@router.get("/stats")
async def get_stats(request: Request):
    cache: Cache = request.app.state.cache
    stats = await cache.stats()
    return JSONResponse(stats)

@router.get("/{key}")
async def get_value(key: str, request: Request):
    cache: Cache = request.app.state.cache
    try:
        value = await cache.get_item(key)
        return JSONResponse({"value": value})
    except KeyError:
        raise HTTPException(404, f"{key=} not found")

@router.put("/{key}")
async def set_value(key: str, intake: Intake, request: Request):
    cache: Cache = request.app.state.cache
    replaced = await cache.put_item(key, intake)
    if replaced:
        return JSONResponse({})
    else:
        return JSONResponse({}, status_code=201)

@router.delete("/{key}")
async def delete_value(key: str, request: Request):
    cache: Cache = request.app.state.cache
    try:
        await cache.delete_item(key)
        return JSONResponse({}, status_code=204)
    except KeyError:
        raise HTTPException(404, f"{key=} not found")

