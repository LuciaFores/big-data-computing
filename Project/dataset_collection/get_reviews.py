import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from tqdm import tqdm
import time
import os

def get_reviews(steam_id, page_number):
    url = f"https://steamcommunity.com/profiles/{steam_id}/recommended/?p={page_number}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    reviews = soup.findAll('div', {'class': 'review_box'})
    return reviews

df_players = pd.read_csv('output_files/players.csv')
steam_ids = set(df_players['steam_id'].tolist())

if not os.path.exists('output_files/game_reviews.csv'):
    print("Creating review file...")
    with open('output_files/game_reviews.csv', 'w') as F:
        writer = csv.writer(F)
        cols = ['steam_id', 'app_id', 'recommended', 'hours_played']
        writer.writerow(cols)
else:
    print("Review file found, next reviews will be appended")

with open('output_files/error_steam_ids.csv', 'w') as F_1:
    writer_1 = csv.writer(F_1)
    cols = ['steam_id']
    writer_1.writerow(cols)

if not os.path.exists('output_files/resolved_steam_ids.csv'):
    print("No resolved steam ids found.")
    with open('output_files/resolved_steam_ids.csv', 'w') as F_2:
        writer = csv.writer(F_2)
        cols = ['steam_id']
        writer.writerow(cols)
else:
    print("Some resolved steam ids found, ids loaded.")
    df_resolved = pd.read_csv('output_files/resolved_steam_ids.csv')
    resolved_steam_ids = df_resolved['steam_id'].tolist()
    steam_ids = list(set(steam_ids) - set(resolved_steam_ids))

with open('output_files/game_reviews.csv', 'a') as F:
    with open('output_files/error_steam_ids.csv', 'a') as F_1:
        with open('output_files/resolved_steam_ids.csv', 'a') as F_2:
            writer = csv.writer(F)
            writer_1 = csv.writer(F_1)
            writer_2 = csv.writer(F_2)
            for steam_id in tqdm(steam_ids, total=len(steam_ids)):
                i = 0
                time.sleep(1.5)
                while True:
                    i += 1
                    try:                   
                        reviews = get_reviews(steam_id, i)
                    except:
                        writer_1.writerow([steam_id])
                        break
                    if reviews != []:
                        for review in reviews:
                            review_data = []
                            review_data.append(str(steam_id))
                            app_id = review.find('a', {'class': 'game_capsule_ctn'})['href'][31:]
                            review_data.append(app_id)
                            recommended = review.find('div', {'class': 'title'}).text
                            review_data.append(recommended)
                            hours_played = review.find('div', {'class': 'hours'}).text
                            hours_played = hours_played.replace('\r', '')
                            hours_played = hours_played.replace('\n', '')
                            hours_played = hours_played.replace('\t', '')
                            review_data.append(hours_played)
                            writer.writerow(review_data)                        
                    else:
                        writer_2.writerow([steam_id])
                        break
                

