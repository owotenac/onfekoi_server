import asyncio
import api_call
from flask import request

baseURL = 'https://api.datatourisme.fr/v1/catalog'

mainFilters = {
        'PointOfInterest' : 'CulturalSite,SportsAndLeisurePlace,NaturalHeritage,ServiceArea',
        "RentalAccommodation" :'RentalAccommodation',
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
    params['filters'] = f'type[in]={mainFilters[type]}'

   #filter
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'


    response = asyncio.run(api_call.api_call(baseURL, customParams=params))
    return api_call.readElements(response)

def searchItems():
    params = {}

    #items
    type = request.args.get('type', type=str)
    if (type is None or type ==''):
        message = "type parameter is required"
        return { "error": message }, 400

    #as we use the catalog API, we filter on the given type
    params['filters'] = f'type[in]={mainFilters[type]}'

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
    return api_call.readElements(response)


def geolocation():

    retrieveOptions = {
        'nbResultsMax' : 20,
        'skipRepresentation' : False
    }

    params = {}

    #items
    type = request.args.get('type', type=str)
    if (type is None or type == ''):
        message = "type parameter is required"
        return { "error": message }, 400

    #as we use the catalog API, we filter on the given type
    params['filters'] = f'type[in]={mainFilters[type]}'

   #filter
    filters = request.args.get('filters', type=str)
    if (filters is not None):
        params['filters'] = f'type[in]={filters}'

    #get only the geolocation
    params['fields'] = 'uuid,label,type,isLocatedAt.geo'

    params['page_size'] = '100'

    response = asyncio.run(api_call.api_call(baseURL, customParams=params))
    return api_call.readElements(response, retrieveOptions)