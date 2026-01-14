import asyncio
import api_call
from flask import request


def getPOI():
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/placeOfInterest'))
    return readPOI(response)

def getPOINext():
    #url
    url = request.args.get('url', type=str)
    if (url is None):
        message = "url parameter is required"
        return { "error": message }, 400

    response = asyncio.run(api_call.api_call(url))
    return readPOI(response)

def readPOI(response):
    r = {'data': [], 'meta': {}}
    nextPage = response['meta']
    cleanResponse(response, r['data'])
    while response['meta'].get('next') and len(r['data']) < 20:
        response = asyncio.run(api_call.api_call(response['meta']['next']))
        cleanResponse(response, r['data'])
        nextPage = response['meta']

    r['meta'] = nextPage
    return r

def cleanResponse(response: dict, r: list) -> list:
    for p in response['objects']:
        #we only want element with main representation (image)
        newProduct = {}
        if (p.get('hasMainRepresentation')):
            #uuid
            newProduct['uuid'] = p['uuid']
            #description
            if (p.get('hasDescription')):
                if (p['hasDescription'][0].get('description')):
                    newProduct['description'] = p['hasDescription'][0]['description']['@fr']
                if (p['hasDescription'][0].get('shortDescription')):
                    newProduct['shortDescription'] = p['hasDescription'][0]['shortDescription']['@fr']
            #name
            newProduct['name'] = p['label']['@fr']
            #image
            newProduct['image'] = p['hasMainRepresentation'][0]['hasRelatedResource'][0]['locator'][0]
            #contact
            if p.get('hasContact'):
                contact = p['hasContact'][0]
                newProduct['contact'] = {'name': contact['legalName']}
                
                for field in ['telephone', 'email', 'homepage']:
                    if contact.get(field):
                        newProduct['contact'][field] = contact[field][0]
            #created by
            if p.get('hasBeenCreatedBy'):
                newProduct['createdBy'] = p['hasBeenCreatedBy']['legalName'][5:] #because we remove the 34 - departement code

            #address
            if (p.get('isLocatedAt')):
                address = p['isLocatedAt'][0]
                addr = {}
                addr['geo'] = address['geo']
                subAddress = address['address'][0]
                addr['zip'] = subAddress.get('postalCode', '')
                addr['city'] = subAddress.get('addressLocality', '')
                addr['streetAddress'] = subAddress.get('streetAddress', '')

                newProduct['address'] = addr

            r.append(newProduct)
    
    return r