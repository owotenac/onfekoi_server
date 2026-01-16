import asyncio
import api_call



def getPOI():
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/placeOfInterest'))
    return api_call.readElements(response)



