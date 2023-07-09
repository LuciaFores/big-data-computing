import requests
import csv
import pandas as pd
from tqdm import tqdm
import time
import os

df = pd.read_csv('output_files/games.csv')
df_tmp = df[df['total_recommendations']>0]
app_ids = df_tmp['steam_appid'].tolist()

players = set()

if not os.path.exists('output_files/players.csv'):
    print("No players found.")
    with open('output_files/players.csv', 'w') as F:
        writer = csv.writer(F)
        cols = ['steam_id', ]
        writer.writerow(cols)
else:
    print("Some players found, ids loaded.")
    df_players = pd.read_csv('output_files/players.csv')
    players = set(df_players['steam_id'].tolist())

with open('output_files/error_appid.csv', 'w') as F_1:
    writer_1 = csv.writer(F_1)
    cols = ['steam_appid', ]
    writer_1.writerow(cols)

if not os.path.exists('output_files/resolved_appid.csv'):
    print('No resolved ids found.')
    with open('output_files/resolved_appid.csv', 'w') as F_2:
        writer_2 = csv.writer(F_2)
        cols = ['steam_appid', ]
        writer_2.writerow(cols)
else:
    print('Already resolved some games ids, removing them from the list...')
    df_resolved = pd.read_csv('output_files/resolved_appid.csv')
    resolved_app_ids = df_resolved['steam_appid'].tolist()
    app_ids = list(set(app_ids) - set(resolved_app_ids))

with open('output_files/players.csv', 'a') as F:
    with open('output_files/error_appid.csv', 'a') as F_1:
        with open('output_files/resolved_appid.csv', 'a') as F_2:
            writer = csv.writer(F)
            writer_1 = csv.writer(F_1)
            writer_2 = csv.writer(F_2)
            for app_id in tqdm(app_ids, total=len(app_ids)):
                url = f'https://store.steampowered.com/appreviews/{app_id}?json=1&language=all&num_per_page=100'
                time.sleep(1)
                try:
                    response = requests.get(url)
                except:     
                    writer_1.writerow([app_id])
                    continue
                if response.status_code == 200:
                    data = response.json()
                    for review in data['reviews']:
                        player_id = review['author']['steamid']
                        if player_id not in players:
                            players.add(player_id)
                            writer.writerow([player_id])
                    writer_2.writerow([app_id])
                else:
                    writer_1.writerow([app_id])