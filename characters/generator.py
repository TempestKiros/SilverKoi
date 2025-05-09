import aiohttp
import random

async def get_random_character():
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
    variables = {
        'page': random.randint(1, 5000)
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://graphql.anilist.co', json={'query': query, 'variables': variables}) as response:
            if response.status == 200:
                data = await response.json()
                character = data['data']['Page']['characters'][0]
                name = character['name']['full']
                image = character['image']['large']
                series = character['media']['nodes'][0]['title']['romaji'] if character['media']['nodes'] else 'Desconocido'
                return {'name': name, 'image': image, 'series': series}
            else:
                return None
