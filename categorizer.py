import vdf
import urllib2
import json
import time
import shelve

filters = ['basic','genres']

URL_BASE = 'http://store.steampowered.com/api/appdetails?appids='
FILTERS = '&filters=' + ','.join(filters)

OWNED_GAMES_URL = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='

ERR_STR = '\t'*4 + 'Error: '

KEY = 'E84A669BBFC93FD2DDBE9DDC4859CB53'
STEAM_ID = '76561197972789961'

shelve = shelve.open('genre_db')

def find_key(d,k):
    for key in d:
        if key == k:
            return d[key]

    return find_key(d[key],k)

def fetch_genres(app_id):
    app = str(app_id)
    app_genres = []
    app_id = str(app_id)

    if app_id in shelve:
        print app_id + ' exists in DB. Using local copy.'
        return shelve[app_id]

    time.sleep(1)
    try:
        res = urllib2.urlopen(URL_BASE+str(app_id)+FILTERS)
        data = json.load(res)
    except:
        print ERR_STR + 'Unable to fetch app: ' + app_id
        #continue
        return None

    if not data[app_id]['success']:
        print ERR_STR + 'Response reports failure: ' + app_id
        return None
        
    app_name =  data[app]['data']['name']

    if data[app]['data']['type'] != "game" and data[app]['data']['type'] != "advertising":
        print ERR_STR + 'App ' + app_name + ' not of type game: ' + app_id + ' ' + data[app]['data']['type']
        return None

    if 'genres' not in data[app]['data']:
        print ERR_STR + 'App ' + app_name + ' - Genres unavailble for app: ' + app_id
        return None

    for entry in data[app]['data']['genres']:
        for field in entry:
            if field == 'description':
                app_genres += [entry[field]]

    print app_name +': ' + app_id + '\n\t' + "New Tags: " + ', '.join(app_genres)

    shelve[app_id] = app_genres

    return app_genres

def fetch_game_ids():
    id_list = []

    try:
        res = urllib2.urlopen(OWNED_GAMES_URL + KEY + '&steamid=' + STEAM_ID + '&format=json')
        data = json.load(res)
    except:
        print ERR_STR + 'Unable to fetch game list: ' + 'N/A'

    for entry in data['response']['games']:
        id_list.append(entry['appid'])

    return id_list

f = vdf.parse(open('sharedconfig.test.vdf'))
d = find_key(f,'apps')
game_list = fetch_game_ids()

for app in game_list:
    built_tags_dict = {}

    genre_list = fetch_genres(app)
    if not genre_list: continue

    for idx,genre in enumerate(genre_list):
        built_tags_dict[str(idx)] = str(genre)

    if app not in d:
        d[app] = {}

    d[app]['tags'] = built_tags_dict

f['UserLocalConfigStore']['Software']['Valve']['Steam']['apps'] = d
s = vdf.dump(f,pretty=True)
new_vdf = open('sharedconfig.vdf','w')
new_vdf.write(s)
shelve.close()
