
import urllib.request
import json


class igdb:

    def __init__(self, apikey):
        self.url = 'https://api-2445582011268.apicast.io'
        self.apikey = apikey
        self.platformlist = ''
        self.headers = {
            'user-key': self.apikey,
            'Accept': 'application/json'
        }
 
    def __request(self, url):
        url = url.replace(' ', '%20')
        print(url + '\n')

        req = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(req)
            
        json_string = response.read().decode()
        parsed_json = json.loads(json_string)

        return parsed_json

    def games(self, args=''):
        'Gets the index of game.'
        return self.__request(self.url + '/games/{}'.format(args))

    def games_id(self, gameid, args=''):
        'Gets specific ids of game.'
        return self.__request(self.url + '/games/{}/{}'.format(gameid, args))

    def games_count(self, args=''):
        'Gets the count of games.'
        return self.__request(self.url + '/games/count/{}'.format(args))

    def games_meta(self, args=''):
        'Gets the fields of game.'
        return self.__request(self.url + '/games/meta/{}'.format(args))

    def platforms(self, args=''):
        'Gets the index of platform.'
        return self.__request(self.url + '/platforms/{}'.format(args))

    def platforms_id(self, platformid, args=''):
        'Gets specific ids of platform.'
        return self.__request(self.url + '/platforms/{}/{}'.format(platformid, args))

    def platforms_count(self, args=''):
        'Gets the count of platforms.'
        return self.__request(self.url + '/platforms/count/{}'.format(args))

    def platforms_meta(self, args=''):
        'Gets the fields of platform.'
        return self.__request(self.url + '/platforms/meta/{}'.format(args))

    def companies(self, args=''):
        'Gets the index of company.'
        return self.__request(self.url + '/companies/{}'.format(args))

    def companies_id(self, companyid, args=''):
        'Gets specific ids of company.'
        return self.__request(self.url + '/companies/{}/{}'.format(companyid, args))

    def companies_count(self, args=''):
        'Gets the count of companies.'
        return self.__request(self.url + '/companies/count/{}'.format(args))

    def companies_meta(self, args=''):
        'Gets the fields of companies.'
        return self.__request(self.url + '/companies/meta/{}'.format(args))

    # ----- helper functions -----
    def get_platforms(self, args=''):
        'Gets all platforms'
        offset = 0
        platforms = []
        temp = self.platforms('?offset={}&limit=50{}'.format(offset, args))
        while len(temp) > 0:
            platforms += temp
            offset += 50
            temp = self.platforms('?offset={}&limit=50{}'.format(offset, args))

        return platforms

    def get_games(self, platformid):
        'Gets all games for a platform'
        games = self.platforms_id(platformid, '?fields=name,games&expand=games')
        games = games[0]['games']

        all_games = [item['name'] for item in games]

        return all_games

    def save_json(self, filename, data):
        'Saves a dictionary to file as json'
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def load_json(self, filename):
        'Loads json from a file'
        with open(filename) as json_data:
            return json.load(json_data)
