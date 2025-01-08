from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app.controllers import url_controller, monitor
from app.models import url
import redis.asyncio
import dotenv
import os


# load environment variables
dotenv.load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_store = redis.asyncio.from_url(f"redis://{os.getenv('REDIS_HOST')}", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_store)
    yield

    #get all keys related to the rate limit and then delete the data or values attached to them 
    rate_limiter_keys = await redis_store.keys("fastapi-limiter:*")
    if rate_limiter_keys:
        await redis_store.delete(*rate_limiter_keys)

    await redis_store.close()

app = FastAPI(
    title="Elropheka url shortener",
    description="URL shortener API by elropheka",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(monitor.RequestMiddleware)

async def rate_limit_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

rate_limiter = RateLimiter(times=100, seconds=86400)

@app.get("/")
async def root(request: Request, _: bool = Depends(RateLimiter(times=10, hours=1, identifier=rate_limit_key))):
    return {"message": "Welcome to our unique url shortener!"}

@app.post("/shorten")
async def shorten_url(request: Request, uri: url.UrlRequest, _: bool = Depends(RateLimiter(times=10, hours=1, identifier=rate_limit_key))):

    try:
        short_url = url_controller.shortUrl(
            requestUrl=request.url,
            url=uri.url
        )
        return {"short_url": short_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/{short_url}")
async def get_original_url(request: Request, short_url: str, _: bool = Depends(RateLimiter(times=20, hours=2, identifier=rate_limit_key))):
    try:
        original_url = url_controller.get_url(short_url=short_url)
        if not original_url:
            raise HTTPException(status_code=404, detail="URL not found")
        return {"original_url": original_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))