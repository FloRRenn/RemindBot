anime_query = '''
        query ($name: String){
          Media(search: $name, type: ANIME) {
            idMal
            description
            title {
              native
              english
            }
            coverImage {
              medium
            }
            startDate {
              year
              month
              day
            }
            rankings {
                type
                rank
                year
                context
            }
            status
            episodes
            duration
            nextAiringEpisode {
              episode
            }
            genres
            studios(isMain: true) {
              nodes {
                name
              }
            }
            siteUrl
            isAdult
          }
        }
        '''

import aiohttp

GRAPHQL_URL = 'https://graphql.anilist.co'    

async def anime_search(anime_name):
    variables = {
            'name': anime_name
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(GRAPHQL_URL, json={'query': anime_query, 'variables': variables}) as r:
            if r.status == 200:
                json = await r.json()
                return json
            else:
                return None

