import tools.DataHandler as dh
import tools.analytics as anal
import tools.authorization as auth
import tools.kmlmap as kmlmap
import os
import time
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import timezone

def hothours(df, figures=False):
    hours =[]
    df["start_date"] = df["start_date"].astype("datetime64")
    for id, item in enumerate(df["start_date"]):
        local_time = item.replace(tzinfo=timezone.utc).astimezone(tz='Europe/Amsterdam')
        hours.append(local_time.hour)
    counts, range = np.histogram(hours, bins=np.max(hours)-np.min(hours))
    sort = np.argsort(counts)[::-1]
    top = sort[0:3]
    print('Hot hours: {}'.format(range[top]))
    if figures:
        plt.bar(counts, bins=range)
        plt.xticks(range)
        plt.show()

def totals(df):
    # Calculate totals for sports
    for sport in ['Ride', 'Run', 'Swim']:
        df_sport = df.loc[(df['type'] == sport) & (df['private'] == False)]
        totals = anal.totals(df_sport)
        time = str(totals['elapsed_time'])
        print(
            '{} totals: distance={:.2f}, kudos={}, avg_kudos={:.2f}, elapsed time={}'.format(sport, totals['distance'],
                                                                                             totals['kudos'],
                                                                                             totals['avg_kudos'], time))
def hindex(df):
    # Calculate H-index per day for sports
    for sport in ['Ride', 'Run', 'Swim']:
        df_day = df.loc[(df['type'] == sport)]
        df_day.index = pd.to_datetime(df_day['start_date'])
        df_day = df_day.resample('D').sum()
        df_day = df_day.drop(df_day.loc[df_day['distance'] == 0].index)
        h_sport = anal.h_index(df_day, figures=False)
        print('%s day h-index: %i' % (sport, h_sport))

    # Calculate tri H-index, a.k.a. H-Trindex
    df_sport = df.loc[(df['type'] == 'Ride') & (df['type'] == 'Run') & (df['type'] == 'Swim')]
    df.index = pd.to_datetime(df['start_date'])
    df = df.resample('D').sum()
    df = df.drop(df.loc[df['distance'] == 0].index)
    h_sport = anal.h_index(df, figures=False)
    print('H-Trindex: %i' % (h_sport))

def speed_per_gear(df):
    # Calculate
    df['moving_time'] = pd.to_timedelta(df['moving_time'])
    df['moving_time'] = df['moving_time'] / np.timedelta64(1, 's')
    gear = df.gear_name.unique()
    for name in gear:
        rowdata = df.loc[(df['gear_name'] == name)].mean()
        speed = (rowdata['distance']/rowdata['moving_time'])*3.6
        print('{}: {:.2f} km/h'.format(name, speed))

############MAIN###############

if __name__ == '__main__':
    # Check if user_access token is available, otherwise do authorisation first.
    if not os.path.isfile(r'tokens\user_access.token'):
       auth.authorize()
    with open(r'tokens\user_access.token', 'r') as file:
        user_token = json.load(file)
    # Check if token is still valid, otherwise refresh token
    if time.time() > user_token['expires_at']:
        user_token = auth.refresh(user_token['refresh_token'])
        print('Token refreshed')
    access_token = user_token['access_token']

    # Create dataHandler object
    data = dh.DataHandler(access_token,  'data')
    # Get latest data
    data.sync()
    df = data.get_data()
    # Show totals per sport
    print('=====Totals=====')
    totals(df)
    # Show h-index of dataset
    print('=====H-Index=====')
    hindex(df)
    # Calculate average speed per gear
    print('=====Average speed per gear=====')
    speed_per_gear(df)
    # Hot hours
    print('=====Hot hours=====')
    hothours(df)

    #Create KML map for heatmap
    # kmlmap.create_kml(access_token, df.loc[df['type'] == 'Ride'])


