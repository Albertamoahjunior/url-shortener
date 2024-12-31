import hashlib
import re
import redis 

r = redis.Redis(host='localhost', port=6379, db=0)

def shortUrl(requestUrl, url):
    """
    Generate a shortened URL using a hashing algorithm.
    """
    hash_object = hashlib.md5( url.encode())
    hex_dig = hash_object.hexdigest()
    short_url = hex_dig[:6]
    r.set(short_url, url)
    short_url = re.sub(r"shorten", "", str(requestUrl)) + short_url
    return short_url

def get_url(short_url):
    """
    Retrieve the original URL from the shortened URL.
    """
    return r.get(short_url)
