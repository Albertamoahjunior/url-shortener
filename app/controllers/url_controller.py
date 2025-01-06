import hashlib
import re
import redis 
from dotenv import load_dotenv
import os

#load environment variables
load_dotenv()

# Set Redis connection details
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

url_store = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def shortUrl(requestUrl, url):
    """
    Generate a shortened URL using a hashing algorithm.
    """
    hash_object = hashlib.md5( url.encode())
    hex_dig = hash_object.hexdigest()
    short_url = hex_dig[:6]
    url_store.set(short_url, url)
    
    short_url = re.sub(r"shorten$", "", str(requestUrl)) + short_url
    return "https://" + short_url

def get_url(short_url):
    """
    Retrieve the original URL from the shortened URL code.
    """
    return url_store.get(short_url)
