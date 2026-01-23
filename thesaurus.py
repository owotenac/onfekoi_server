import aiohttp
import asyncio
from flask import request
import json


async def extract_thesaurus(url: str = None):
    headers = {
        "Accept": "application/json",
        "X-API-Key": "72f08dd4-6eca-443b-aba3-5d650abc28da"
    }
    params = {
        'lang': 'fr',
        'fields': 'key,name'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            return data

def run():
    r = {'data': [], 'meta': {}}

    url = 'https://api.datatourisme.fr/v1/thesaurus/Class'
    response = asyncio.run(extract_thesaurus(url))
    nextPage = response.get('meta', {})
    r['data'].extend(response['objects'])
    
    while response['meta'].get('next') :
        response = asyncio.run(extract_thesaurus(response['meta']['next']))
        r['data'].extend(response['objects'])  
        nextPage = response.get('meta', {})

    r['meta'] = nextPage
    return r


def main():
    r = run()

    mapping = {}
    for tag in r.get('data', []):
        key = tag.get('key')
        label = tag.get('name', {}).get('@fr', '')
        mapping[key] = label

    with open('thesaurusdata.py', 'w') as f:
        f.write(json.dumps(mapping, indent=4, ensure_ascii=True))

if __name__ == "__main__":
    main()