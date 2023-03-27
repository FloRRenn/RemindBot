import aiohttp
anime_query = '''
        query ($name: String){
          Media(search: $name, type: ANIME) {
            idMal
            description(asHtml: false)
            title {
              native
              romaji
            }
            bannerImage
            startDate {
              year
              month
              day
            }
            status
            episodes
            duration
            nextAiringEpisode {
              episode
            }
            characters(role: MAIN) {
              nodes {
                name {
                  full
                }
              }
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


GRAPHQL_URL = 'https://graphql.anilist.co'


async def anime_search(anime_name):
  variables = {
      'name': anime_name
  }
  async with aiohttp.ClientSession() as session:
      async with session.post(GRAPHQL_URL, json={'query': anime_query, 'variables': variables}) as r:
          if r.status == 200:
              json = await r.json()
              return json["data"]["Media"]
          else:
            print(r.content)
            print(r.status)
            return None


async def studio_search(studio_name):
  pass
  