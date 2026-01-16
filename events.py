import asyncio
import api_call

def getEvents():
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/entertainmentAndEvent'))
    return api_call.readElements(response)
