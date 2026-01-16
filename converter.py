

def get_localized_text(data, field, lang='@fr', default='') -> str:
    """Safely extract localized text from nested structure."""
    if not data or not isinstance(data, dict):
        return default
    field_data = data.get(field)
    if isinstance(field_data, dict):
        return field_data.get(lang, default)
    return default


# def cleanResponses(response: dict, newResponse: list):
#     for p in response['objects']:
#         newProduct = cleanResponse(p)
#         if len(newProduct) > 0:
#             newResponse.append(newProduct)

def cleanResponses(response: dict) -> list:
    return [
        newProduct for p in response['objects']
        if len(newProduct := cleanResponse(p)) > 0
    ]

# def cleanResponses(response: dict, newResponse: list):
#     cleaned = [cleanResponse(p) for p in response['objects']]
#     newResponse.extend([p for p in cleaned if len(p) > 0])

    #return r

def cleanResponse(p: dict) -> list:
    #we only want products with main representation (image)
    newProduct = {}
    if (p.get('hasMainRepresentation')):
        #uuid
        newProduct['uuid'] = p['uuid']

        # description
        if p.get('hasDescription') and len(p['hasDescription']) > 0:
            desc = p['hasDescription'][0]
            #description
            newProduct['description'] = get_localized_text(desc, 'description')
            newProduct['shortDescription'] = get_localized_text(desc, 'shortDescription')

        #name
        newProduct['name'] = get_localized_text(p, 'label')
        #image
        newProduct['image'] = p['hasMainRepresentation'][0]['hasRelatedResource'][0]['locator'][0]
        #contact
        if p.get('hasContact') and len(p['hasContact']) > 0:
            contact = p['hasContact'][0]
            newProduct['contact'] = {'name': contact.get('legalName', '')}
            
            for field in ['telephone', 'email', 'homepage']:
                if contact.get(field):
                    newProduct['contact'][field] = contact[field][0]
        #created by
        if p.get('hasBeenCreatedBy'):
            newProduct['createdBy'] = p['hasBeenCreatedBy']['legalName'][5:] #because we remove the 34 - departement code

        #address
        if (p.get('isLocatedAt')):
            location = extract_location(p)
            if location:
                newProduct['address'] = location

        #offer
        if (p.get('offers')):
            offer = p['offers']
            payment_methods = extract_payment_methods(offer[0])
            if payment_methods:
                newProduct['acceptedPaymentMethod'] = payment_methods

        #picture
        if (p.get('hasRepresentation')):
            representations = extract_representations(p)
            if representations:
                newProduct['hasRepresentation'] = representations

    return newProduct


def extract_payment_methods(data, lang='@fr'):
    """Extract payment methods as a list of {label, key} dicts."""
    methods = data.get('acceptedPaymentMethod', [])
    
    return [
        {
            'label': method.get('label', {}).get(lang, ''),
            'key': method.get('key', '')
        }
        for method in methods
        if isinstance(method, dict) and (method.get('key') or method.get('label'))
    ]

def extract_representations(data, lang='@fr'):
    """Extract representations with credits, title, and locator."""
    if not data.get('hasRepresentation'):
        return []
    
    result = []
    for rep in data['hasRepresentation']:
        if not isinstance(rep, dict):
            continue
        
        # Extract credits and title from hasAnnotation
        credits = ''
        title = ''
        if (rep.get('hasAnnotation') and 
            len(rep['hasAnnotation']) > 0 and 
            isinstance(rep['hasAnnotation'][0], dict)):
            
            annotation = rep['hasAnnotation'][0]
            
            # Get credits (first item from list)
            if annotation.get('credits') and len(annotation['credits']) > 0:
                credits = annotation['credits'][0]
            
            # Get localized title
            if annotation.get('title') and isinstance(annotation['title'], dict):
                title = annotation['title'].get(lang, '')
        
        # Extract locator from hasRelatedResource
        locator = ''
        if (rep.get('hasRelatedResource') and 
            len(rep['hasRelatedResource']) > 0 and 
            isinstance(rep['hasRelatedResource'][0], dict)):
            
            resource = rep['hasRelatedResource'][0]
            if resource.get('locator') and len(resource['locator']) > 0:
                locator = resource['locator'][0]
        
        # Only add if we have at least a locator
        if locator:
            result.append({
                'credits': credits,
                'title': title,
                'locator': locator
            })
    
    return result

def extract_location(data, lang='@fr'):
    """Extract location with geo coordinates and simplified address."""
    if not data.get('isLocatedAt') or len(data['isLocatedAt']) == 0:
        return None
    
    location_data = data['isLocatedAt'][0]
    if not isinstance(location_data, dict):
        return None
    
    result = {}
    
    # Extract geo coordinates
    if location_data.get('geo') and isinstance(location_data['geo'], dict):
        geo = location_data['geo']
        result['geo'] = {
            'latitude': geo.get('latitude', ''),
            'longitude': geo.get('longitude', '')
        }
    
    # Extract simplified address
    if (location_data.get('address') and 
        len(location_data['address']) > 0 and 
        isinstance(location_data['address'][0], dict)):
        
        addr = location_data['address'][0]
        
        # Get street address (first item from list)
        street_address = ''
        if addr.get('streetAddress') and len(addr['streetAddress']) > 0:
            street_address = addr['streetAddress'][0]

        result['streetAddress'] = street_address
        result['zip'] = addr.get('postalCode', '')
        result['city'] = addr.get('addressLocality', '')
    
    # Only return if we have at least some data
    return result if result else None