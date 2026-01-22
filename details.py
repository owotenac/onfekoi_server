import asyncio
import api_call
from flask import request

def getDetails():
   #uuid
    uuid = request.args.get('uuid', type=str)
    if (uuid is None):
        message = "uuid parameter is required"
        return { "error": message }, 400
        
    response = asyncio.run(api_call.api_call(f'https://api.datatourisme.fr/v1/catalog/{uuid}', {
        "fields" : "uuid,label,hasMainRepresentation,hasDescription,hasContact,hasBeenCreatedBy,isLocatedAt,hasRepresentation,hasFeature"
    }))
    return api_call.readDetails(response)