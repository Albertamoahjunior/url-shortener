from fastapi import FastAPI, Request
from app.controllers import url_controller
from app.models import url

app = FastAPI(
    title="My custom url shortener API",
    description="This is a custom url shortener API for testing purposes",  
    version="1.0.0",  # Version of the API
)

@app.get("/")
async def root():
    return {"message": "Welcome our unique url shortener!"}

@app.post("/shorten")
async def shorten_url(request: Request, uri: url.UrlRequest):
    """
    Shorten a given URL.
    """
    return {"short_url": url_controller.shortUrl(requestUrl='shorten.elropheka.online/', url=uri.url)}

@app.get("/{short_url}")
async def get_original_url(short_url: str):
    """
    Retrieve the original URL from the shortened URL.
    """
    return {"original_url": url_controller.get_url(short_url=short_url)}
