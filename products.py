import asyncio
import api_call

def getProducts():
    response = asyncio.run(api_call.api_call('https://api.datatourisme.fr/v1/product'))

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
        #we only want products with main representation (image)
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
            if (p.get('hasContact')):
                newProduct['contact'] = p['hasContact'][0]

            r.append(newProduct)
    
    return r