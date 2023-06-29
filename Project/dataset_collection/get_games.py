# Import needed libraries for the script
import requests
import json
import pandas as pd
from steam import Steam
from tqdm import tqdm
import csv
import time
import os


def get_game_info(app_id):
    """
    This function takes the app_id of a game and returns the information
    about the game from the Steam API.
    """ 
    try:
        url = f'http://store.steampowered.com/api/appdetails?appids={app_id}'
        response = requests.get(url)
        data = response.json()
        if data == None:
            with open('output_files/error_log.txt', 'a') as F:
                F.write(f'{app_id}\n')
            return {}
        if data[str(app_id)]['success']:
            return data[str(app_id)]['data']
        else:
            #print('Error: Unable to retrieve game information.')
            return {}
    except requests.exceptions.RequestException as e:
        print('Error: ', e)
        with open('output_files/error_log.txt', 'a') as F:
            F.write(f'{app_id}\n')
        return {}


# Set the API key for Steam
KEY = '0BAEAA44F5C3C9967C53E41AE9B50F25'
steam = Steam(KEY)

# Check for the existence of the Steam application file
# If not present, download it
if not os.path.exists('output_files/apps.csv'):
    print('Steam application file not found. Downloading it...')
    URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    r = requests.get(url=URL)
    apps_data = r.json()
    apps_data = apps_data['applist']['apps']
    with open('output_files/apps.json', 'w') as F:
        json.dump(apps_data, F)
    df = pd.read_json('output_files/apps.json')
    df.to_csv('output_files/apps.csv', index=None)
else:
    print('Steam application file found. Loading it...')

# Read the Steam application file as dataframe
# and get only the identifier of the applications
df = pd.read_csv('output_files/apps.csv')
app_ids = df['appid']

# Loop over the entire list of application to find games and dlc
with open('output_files/games.csv', 'w') as F:
    writer = csv.writer(F)
    cols = ['name', 'steam_appid', 'type', 'about_the_game', 'short_description', 'total_recommendations', ]
    writer.writerow(cols)
    for i, row in tqdm(app_ids.to_frame().iterrows(), total = app_ids.shape[0]):
        if i%20 == 0:
            time.sleep(15)
        app_id = row['appid']
        game_info = get_game_info(app_id)
        if game_info != {}:
            if game_info['type'] == 'game' or game_info['type'] == 'dlc':
                data = []
                data.append(game_info['name'])
                data.append(game_info['steam_appid'])
                data.append(game_info['type'])
                data.append(game_info['about_the_game'])
                data.append(game_info['short_description'])
                try:
                    data.append(game_info['recommendations']['total'])
                except KeyError:
                    data.append(0)
                writer.writerow(data)

