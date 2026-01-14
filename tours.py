import asyncio
import api_call

def getTours():
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/tour'))
    return response    