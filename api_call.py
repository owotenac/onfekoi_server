from cachetools import TTLCache
import hashlib
import aiohttp
import asyncio
import converter
from flask import request
import json

# Create a cache with max 100 items, 1 hour TTL (3600 seconds)
api_cache = TTLCache(maxsize=100, ttl=3600)

def get_cache_key(url, customParams):
    """Generate a unique cache key from URL"""
    return hashlib.md5(url.encode() + json.dumps(customParams).encode() ).hexdigest()

async def api_call(url:str, customParams: dict = None):
    use_cache=True
    """API call with caching support"""
    cache_key = get_cache_key(url, customParams)
    
    if use_cache and cache_key in api_cache:
        print(f"Cache hit for {url} and {json.dumps(customParams)}")
        return api_cache[cache_key]
    
    print(f"Cache miss for {url} and {json.dumps(customParams)}")
    response = await p_api_call(url, customParams)
    api_cache[cache_key] = response
    return response


async def p_api_call(url: str, customParams: dict = None):
    headers = {
        "Accept": "application/json",
        "X-API-Key": "72f08dd4-6eca-443b-aba3-5d650abc28da"
    }
    params = {
        'department': '34',
        'lang': 'fr',
        **(customParams or {})  # Unpack customParams, or empty dict if None
    }
  
        
    print(f"Fetching URL: {url} with params: {params}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data
        

def getNextPage():
    #url
    url = request.args.get('url', type=str)
    if (url is None):
        message = "url parameter is required"
        return { "error": message }, 400

    response = asyncio.run(api_call(url))
    return readElements(response)

import time

def readElements(response):
    start = time.time()
    r = {'data': [], 'meta': {}}
    nextPage = response.get('meta', {})
    
    r['data'].extend(converter.cleanResponses(response))
    
    while response['meta'].get('next') and len(r['data']) < 5:
        response = asyncio.run(api_call(response['meta']['next']))
        r['data'].extend(converter.cleanResponses(response))  
        nextPage = response.get('meta', {})

    r['meta'] = nextPage
    end = time.time()    
    print(f"Execution time: {end - start:.4f} seconds")
    return r

def readDetails(response):
    
    newResponse = converter.cleanResponse(response)
    return newResponse