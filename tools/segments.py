import numpy as np
import pandas as pd
import time
from tqdm import tqdm
import os.path
from stravalib import Client

def segmentlist(user_token, df):
    client = Client(access_token=user_token)
    df_segments = pd.DataFrame()
    df_segments['id'] = np.nan # make the id column
    idx = 0
    for a, row in tqdm(df.iterrows(), total=df.shape[0],desc='Creating all segments list'):
        if idx % 550 == 0 and idx > 1:  # To prevent exceeding strava limits
            print('Waiting for STRAVA API limits.')
            time.sleep(900)
        id = row['id']
        last_act = client.get_activity(activity_id=id, include_all_efforts=True) # Get activity

        for i in range(len(last_act.segment_efforts)):
            segment_id = last_act.segment_efforts[i].segment.id
            if sum(df_segments['id'].isin([segment_id])) == 0:  # Only for unique segments
                entry = {'id': last_act.segment_efforts[i].segment.id,
                         'name': last_act.segment_efforts[i].name,
                         'distance': float(last_act.segment_efforts[i].distance.num),
                         'activity_type': str(last_act.type),
                         'average_grade': last_act.segment_efforts[i].segment.average_grade,
                         'efforts': int(last_act.segment_efforts[i].segment.leaderboard.entry_count),
                        }

                for j in reversed(range(len(last_act.segment_efforts[i].segment.leaderboard.entries))):
                    if str(last_act.segment_efforts[i].segment.leaderboard.entries[j].athlete_name) == 'Bouke S.':
                        entry['rank'] = last_act.segment_efforts[i].segment.leaderboard.entries[j].rank
                        entry['elapsed_time'] = last_act.segment_efforts[i].segment.leaderboard.entries[j].elapsed_time
                        entry['pr_date'] = last_act.segment_efforts[i].segment.leaderboard.entries[j].start_date_local
                        break

                df_segments = df_segments.append(entry, ignore_index=True)

            if idx == 1:
                test = 100

        idx += 1

    df_segments = df_segments.sort_values(by=['kom_rank'])
    df_segments.to_excel(r'data\Segmentsv2.xlsx')
    return df_segments

# Later, make one function which combines segmentlist and segmentrating
def segmentrating(user_token, df_segments):
    client = Client(access_token=user_token)
    for idx in range(20): # len(df_segments) but for no, only first 20 segments
        segment_id = df_segments['id'][idx]
        segment = client.get_segment_leaderboard(segment_id, gender=None)

        if len(segment.entries) == 15:
            entry = {'type': str(segment.kom_type),
                 'effort_count': int(segment.effort_count),
                 'rank': int(segment.entries[12].rank)} # Check if always at 12

        #df_segments.to_excel(r'data\Segments.xlsx')