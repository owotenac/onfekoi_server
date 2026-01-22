import asyncio
import api_call
from flask import request


def getPOI():
   #filter
    filtersParam = {}
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        filtersParam = {
            'filters' : f'type[in]={filters}'
        }

    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/placeOfInterest', customParams=filtersParam))
    return api_call.readElements(response)
    

def searchPOI():
   #search
    search = request.args.get('search', type=str)
    if (search is None):
        message = "search parameter is required"
        return { "error": message }, 400
        
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/placeOfInterest' , 
                           customParams= {
                               'search' : search
                           }))
    return api_call.readElements(response)

