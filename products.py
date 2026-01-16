import asyncio
import api_call

def getProducts():
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/product'))
    return api_call.readElements(response)

    