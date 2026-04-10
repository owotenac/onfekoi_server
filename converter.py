import thesaurusdata
from catalog import mainFilters


def get_localized_text(data, field, lang='@fr', default='') -> str:
    """Safely extract localized text from nested structure."""
    if not data or not isinstance(data, dict):
        return default
    field_data = data.get(field)
    if isinstance(field_data, dict):
        return field_data.get(lang, default)
    return default

def cleanResponses(response: dict, retrieveOptions) -> list:
    return [
        newProduct for p in response['objects']
        if len(newProduct := cleanResponse(p, retrieveOptions)) > 0
    ]

def cleanResponse(p: dict, retrieveOptions) -> list:


    try:    
        newProduct = {}
        newProduct['uuid'] = p['uuid']
        #name
        newProduct['name'] = get_localized_text(p, 'label')

        if p.get('hasMainRepresentation'):
            #image
            newProduct['image'] = p['hasMainRepresentation'][0]['hasRelatedResource'][0]['locator'][0]


        # description
        has_desc = p.get('hasDescription')
        if has_desc and len(has_desc) > 0:
            desc = has_desc[0]
            #description
            newProduct['description'] = get_localized_text(desc, 'description')
            newProduct['shortDescription'] = get_localized_text(desc, 'shortDescription')
        # else:
        #     return {}

        #contact
        newProduct['contact'] = {}
        has_contact = p.get('hasContact')
        if has_contact and len(has_contact) > 0:
            contact = has_contact[0]
            newProduct['contact'] = {'name': contact.get('legalName', '')}
            
            for field in ['telephone', 'email', 'homepage']:
                if field in contact:
                    newProduct['contact'][field] = contact[field][0]
        #created by
        created_by = p.get('hasBeenCreatedBy')
        if created_by:
            newProduct['createdBy'] = created_by['legalName']

        #address
        isLocatedAt = p.get('isLocatedAt')
        if (isLocatedAt):
            location = extract_location(p)
            if location:
                newProduct['address'] = location
            #opening hours are located in isLocatedAt
            opening = extract_openingInfo(isLocatedAt[0])
            if opening:
                newProduct['openingInfo'] = opening

        #offer
        offers = p.get('offers')
        if offers and len(offers) > 0:
            offer = offers[0]
            payment_methods = extract_methods(offer, 'acceptedPaymentMethod')
            if payment_methods:
                newProduct['acceptedPaymentMethod'] = payment_methods

        #picture
        if (p.get('hasRepresentation')):
            representations = extract_representations(p)
            if representations:
                newProduct['hasRepresentation'] = representations

        features = p.get('hasFeature')
        if (features) and len(features) > 0:
            f = features[0]
            feature_methods = extract_methods(f, 'features')
            if feature_methods:
                newProduct['features'] = feature_methods

        types = p.get('type')
        if (types) and len(types) > 0:
            #we try to find the main type
            newProduct['mainType'] = get_main_type(types)
            #we convert the thesauraus for readable content
            converted_types = extract_thesaurus(types)
            if (converted_types):
                newProduct['type'] = converted_types

        #practice
        practice_conditions = extract_practice_condition(p)
        if practice_conditions:
            newProduct['practiceCondition'] = practice_conditions

        #we make sure hasReprensation has only images, and move gpx or pdf file to the practice condition
        gpx_files = []
        if (newProduct.get('hasRepresentation')):
            gpx_files = [rep for rep in newProduct['hasRepresentation'] if rep['locator'].endswith('.gpx') or rep['locator'].endswith('.pdf')]
            newProduct['hasRepresentation'] = [rep for rep in newProduct['hasRepresentation'] if rep['type'] == 'image' or rep['locator'].endswith('.png') or rep['locator'].endswith('.jpg')]
        if (gpx_files and newProduct.get('practiceCondition')):
            newProduct['practiceCondition']['hasRepresentation'] = gpx_files
        elif (gpx_files):
            newProduct['practiceCondition'] = {'hasRepresentation' : gpx_files}


        return newProduct
    except Exception as e:
        print(e)
        return {}


def extract_methods(data, key, lang='@fr'):
    """Extract methods as a list of {label, key} dicts."""
    methods = data.get(key, [])
    
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
        credits: str = ''
        title: str = ''
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
        
        # Extract locator and mime type from hasRelatedResource
        if rep.get('hasRelatedResource') and isinstance(rep['hasRelatedResource'], list):
            for resource in rep['hasRelatedResource']:
                if not isinstance(resource, dict):
                    continue
                
                res_type: str = ''
                if (resource.get('hasMimeType') and 
                    isinstance(resource['hasMimeType'], list) and 
                    len(resource['hasMimeType']) > 0 and 
                    isinstance(resource['hasMimeType'][0], dict)):
                    
                    mime_label = resource['hasMimeType'][0].get('label')
                    if isinstance(mime_label, dict):
                        res_type = mime_label.get(lang, '')

                if resource.get('locator') and isinstance(resource['locator'], list) and len(resource['locator']) > 0:
                    locator = resource['locator'][0]
                        
                    result.append({
                        'credits': credits,
                        'title': title,
                        'locator': locator,
                        'type': res_type
                    })
    
    return result


def extract_practice_condition(data, lang='@fr'):
    """Extract practice conditions including duration, locomotion mode, difficulty and representations."""
    if not data.get('hasPracticeCondition') or len(data['hasPracticeCondition']) == 0:
        return None

    cond = data['hasPracticeCondition'][0]    
        
    result = {}
    if 'durationDays' in cond:
        result['durationDays'] = str(cond['durationDays'])
        
    if 'duration' in cond:
        result['duration'] = str(cond['duration'])
        
    if cond.get('hasLocomotionMode') and len(cond['hasLocomotionMode']) > 0:
        mode = cond['hasLocomotionMode'][0]
        if isinstance(mode, dict):
            result['locomotionMode'] = {
                'label': mode.get('label', {}).get(lang, ''),
                'key': mode.get('key', '')
            }
            
    if cond.get('hasDifficultyLevel') and len(cond['hasDifficultyLevel']) > 0:
        level = cond['hasDifficultyLevel'][0]
        if isinstance(level, dict):
            result['difficultyLevel'] = {
                'label': level.get('label', {}).get(lang, ''),
                'key': level.get('key', '')
            }
    #here we "should" have the gpx file
    if cond.get('hasRepresentation'):
        reps = extract_representations(cond, lang)
        if reps:
            result['hasRepresentation'] = reps
    # else:
    #     #sometimes we have the gpx here => move it to praticalcondition
    #     if (resource['locator'][0].endswith('.gpx')):
    #         r = {}
    #         r['locator'] = resource['locator'][0]
    #         data['hasPracticeCondition'][0]['hasRepresentation'] = []
    #         data['hasPracticeCondition'][0]['hasRepresentation'].append(r)
                
       
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
        street_address: str = ''
        if addr.get('streetAddress') and len(addr['streetAddress']) > 0:
            street_address = addr['streetAddress'][0]

        result['streetAddress'] = street_address
        result['zip'] = addr.get('postalCode', '')
        result['city'] = addr.get('addressLocality', '')

    
    
    # Only return if we have at least some data
    return result if result else None

def extract_openingInfo(data, lang='@fr'):
    """Extract opening Info """
    node = data.get('openingHoursSpecification')
    if not node or len(node) == 0:
        return None
    
    openingInfo = node[0]
    if not isinstance(openingInfo, dict):
        return None
    
    info: str = ''
    if openingInfo.get('additionalInformation') and isinstance(openingInfo['additionalInformation'], dict):
        info = openingInfo['additionalInformation'].get(lang, '')

    result = {}
    result['validFrom'] = openingInfo['validFrom']
    result['validThrough'] = openingInfo['validThrough']
    result['additionalInformation'] = info

    return result

def extract_thesaurus(types: dict):
    """Extract thesaurus types as localized labels."""
    types_list = []
    for tag in types:
        key = thesaurusdata.thesaurusData.get(tag)
        if key and tag not in thesaurusdata.thesaurusDataToExclude: #we remove the useless tags
            t = {}
            t['key'] = tag
            t['label'] = key
            types_list.append(t)

    return types_list

def get_main_type(api_types):
    """
    Extract the main type from API response types.
    
    Args:
        api_types: List of types from API response
        
    Returns:
        Main type string if found, None otherwise
    """
    api_types_set = set(api_types)
    
    for main_type, subtypes in mainFilters.items():
        # Check if main type itself is in the response
        if main_type in api_types_set and main_type not in thesaurusdata.thesaurusDataToExclude: #we remove the useless tags
            return main_type
        
        # Check if any subtype matches
        subtypes_set = set(subtypes.split(','))
        if api_types_set & subtypes_set:  # Set intersection
            return main_type
    
    return None

import math

def getBoundingBox(lat: float, lon: float, distanceKm: float = 10.0):
    lat = float(lat)
    lon = float(lon)

    latOffset = distanceKm / 111.0
    lonOffset = distanceKm / (111.0 * math.cos(math.radians(lat)))

    north = lat + latOffset
    south = lat - latOffset
    east  = lon + lonOffset
    west  = lon - lonOffset

    return f"{north},{west},{south},{east}"
