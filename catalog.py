import asyncio
import api_call
from flask import request
import converter

baseURL = 'https://api.datatourisme.fr/v1/catalog'

mainFilters = {
        'PointOfInterest' : 'CulturalSite,SportsAndLeisurePlace,NaturalHeritage,ServiceArea',
        "RentalAccommodation" :'RentalAccommodation,Accommodation,LodgingBusiness',
        'Tour' : 'CyclingTour,WalkingTour,RoadTour',
        'FoodEstablishment' : 'FoodEstablishment,Producer',
        'EntertainmentAndEvent' : 'CulturalEvent,TheaterEvent,SportsEvent,Practice'
        }


def getItems():
    params = {}

    #items
    type = request.args.get('type', type=str)
    if (type is None or type == ''):
        message = "type parameter is required"
        return { "error": message }, 400

    #as we use the catalog API, we filter on the given type
    filters = mainFilters.get(type, "")
    if (filters ==''):
        message = "type is unknown"
        return { "error": message }, 400

    params['filters'] = f'type[in]={filters}'

   #filter
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'


    response = asyncio.run(api_call.api_call(baseURL, customParams=params))
    if isinstance(response, tuple) and response[1] != 200:
        return response
        
    return api_call.readElements(response)

def searchItems():
    params = {}

    #items
    type = request.args.get('type', type=str)
    if (type is None or type ==''):
        message = "type parameter is required"
        return { "error": message }, 400

    #as we use the catalog API, we filter on the given type
    filters = mainFilters.get(type, "")
    if (filters ==''):
        message = "type is unknown"
        return { "error": message }, 400

    params['filters'] = f'type[in]={filters}'

   #filter
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'

    #search
    search = request.args.get('search', type=str)
    if (search is None):
        message = "search parameter is required"
        return { "error": message }, 400
    params['search'] = search

    response = asyncio.run(api_call.api_call(baseURL , 
                           customParams= params))
    if isinstance(response, tuple) and response[1] != 200:
        return response
        
    return api_call.readElements(response)


def geolocation():

    retrieveOptions = {
        'nbResultsMax' : 100,
        'skipRepresentation' : False
    }

    params = {}

    #items
    type = request.args.get('type', type=str)
    if (type is None or type == ''):
        message = "type parameter is required"
        return { "error": message }, 400

    lat = request.args.get("lat", type=str)
    lon = request.args.get("lon", type=str)
    if (lat is None or lon is None):
        message = "Missing geolocation parameters"
        return { "error": message }, 400

    #as we use the catalog API, we filter on the given type if we have it
    if (type != "ALL"):
        params['filters'] = f'type[in]={mainFilters[type]}'

   #filter
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'

    #bouding rect for geolocation
    bouding_box = converter.getBoundingBox(lat, lon)
    params['geo_bounding'] = bouding_box

    #get only the geolocation
    params['fields'] = 'uuid,label,type,isLocatedAt.geo,hasDescription'

    params['page_size'] = retrieveOptions['nbResultsMax']

    response = asyncio.run(api_call.api_call(baseURL, customParams=params))
    if isinstance(response, tuple) and response[1] != 200:
        return response
    
    return api_call.readElements(response, retrieveOptions)