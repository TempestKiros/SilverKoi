import aiohttp
import random
import asyncio

async def get_random_character(max_retries=3):
    query = '''
    query ($page: Int) {
      Page(page: $page, perPage: 1) {
        characters {
          name {
            full
          }
          image {
            large
          }
          media {
            nodes {
              title {
                romaji
              }
            }
          }
        }
      }
    }
    '''

    for _ in range(max_retries):
        variables = {
            'page': random.randint(1, 5000)
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://graphql.anilist.co', json={'query': query, 'variables': variables}) as response:
                if response.status == 200:
                    data = await response.json()
                    characters = data.get('data', {}).get('Page', {}).get('characters', [])
                    if not characters:
                        continue
                    
                    char = characters[0]
                    name = char.get('name', {}).get('full', 'Desconocido')
                    image = char.get('image', {}).get('large', '')
                    series_list = char.get('media', {}).get('nodes', [])
                    series = series_list[0]['title']['romaji'] if series_list else 'Desconocido'

                    if name and image:
                        return {'name': name, 'image': image, 'series': series}
                else:
                    await asyncio.sleep(1)  # espera antes de reintentar

    return {'name': 'Desconocido', 'image': '', 'series': 'Desconocido'}
