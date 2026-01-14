from cachetools import TTLCache
import hashlib
import aiohttp
import requests
from urllib.request import urlparse

# Create a cache with max 100 items, 1 hour TTL (3600 seconds)
api_cache = TTLCache(maxsize=100, ttl=3600)

def get_cache_key(url):
    """Generate a unique cache key from URL"""
    return hashlib.md5(url.encode()).hexdigest()

async def api_call(url:str, use_cache=True):
    """API call with caching support"""
    cache_key = get_cache_key(url)
    
    if use_cache and cache_key in api_cache:
        print(f"Cache hit for {url}")
        return api_cache[cache_key]
    
    print(f"Cache miss for {url}")
    response = await p_api_call(url)
    api_cache[cache_key] = response
    return response


async def p_api_call(url: str):
    headers = {
        "Accept": "application/json",
        "X-API-Key": "72f08dd4-6eca-443b-aba3-5d650abc28da"
    }
    params = {
        'department': '34',
        'lang': 'fr'
    }

    print(f"Fetching URL: {url} with params: {params}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data