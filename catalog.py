import asyncio
import api_call
from flask import request

catalogUrlMap = {
    'catalog': 'https://api.datatourisme.fr/v1/catalog',
    'poi': 'https://api.datatourisme.fr/v1/placeOfInterest',
    'events': 'https://api.datatourisme.fr/v1/entertainmentAndEvent',
    'tours': 'https://api.datatourisme.fr/v1/tour'
}

def getItems():
    #items
    type = request.args.get('type', type=str)
    if (type is None):
        message = "type parameter is required"
        return { "error": message }, 400
        
   #filter
    params = {}
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'

    if (type not in catalogUrlMap):
        message = "type parameter is invalid"
        return { "error": message }, 400
    
    url = catalogUrlMap[type]

    response = asyncio.run(api_call.api_call(url, customParams=params))
    return api_call.readElements(response)

def searchItems():
    #items
    type = request.args.get('type', type=str)
    if (type is None):
        message = "type parameter is required"
        return { "error": message }, 400

    params = {}
    #search
    search = request.args.get('search', type=str)
    if (search is None):
        message = "search parameter is required"
        return { "error": message }, 400
    params['search'] = search

    if (type not in catalogUrlMap):
        message = "type parameter is invalid"
        return { "error": message }, 400
   
    url = catalogUrlMap[type]

   #filter
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'

    response = asyncio.run(api_call.api_call(url , 
                           customParams= params))
    return api_call.readElements(response)