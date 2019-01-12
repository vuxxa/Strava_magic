import tools.DataHandler as dh
import tools.analytics as anal
import tools.authorization as auth
import tools.segments as seg
import tools.kmlmap as kmlmap
import os
import time
import json

#Check if user_access token is available, otherwise do authorisation first.
if not os.path.isfile(r'tokens\user_access.token'):
   auth.authorize()
with open(r'tokens\user_access.token', 'r') as file:
    user_token = json.load(file)
#Check if token is still valid, otherwise refresh token
if time.time() > user_token['expires_at']:
    user_token = auth.refresh(user_token['refresh_token'])
    print('Token refreshed')
access_token = user_token['access_token']

# create dataHandler object
data = dh.DataHandler(access_token,  'data')
# Get latest data
data.sync()
df = data.get_data()

# Calculate H-index and totals for sports
for sport in ['Ride', 'Run', 'Swim']:
    df_sport = df.loc[df['type'] == sport]
    totals = anal.totals(df_sport)
    h_sport = anal.h_index(df_sport, figures=False)
    print('%s h-index: %i' %(sport, h_sport))
    time = str(totals['elapsed_time'])
    print('{} totals: distance={:.2f}, kudos={}, avg_kudos={:.2f}, elapsed time={}'.format(sport, totals['distance'], totals['kudos'], totals['avg_kudos'], time))

# df_segments = seg.segmentlist(access_token, df.loc[df['manual'] == 0]) # Takes a lot of time
import pandas as pd
df_segments = pd.read_excel(r'data\Segments.xlsx')
df_segments = seg.segmentrating(access_token, df_segments) # Takes again a lot of time
#Create KML map for heatmap
# kmlmap.create_kml(access_token, df.loc[df['type'] == 'Ride'])


