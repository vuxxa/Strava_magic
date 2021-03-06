import tools.DataHandler as dh
import tools.authorization as auth
import tools.segments2 as seg
import os
import time
import json

if __name__ == '__main__':
    # Check if user_access token is available, otherwise do authorisation first.
    if not os.path.isfile(os.path.join('tokens', 'user_access.token')):
        auth.authorize()
    with open(os.path.join('tokens', 'user_access.token'), 'r') as file:
        user_token = json.load(file)
    # Check if token is still valid, otherwise refresh token
    if time.time() > user_token['expires_at']:
        user_token = auth.refresh(user_token['refresh_token'])
        print('Token refreshed')
    access_token = user_token['access_token']

    # Create dataHandler object
    data = dh.DataHandler(access_token, 'data')
    # Get latest data
    data.sync()
    df = data.get_data()

    # Create segments list data handeler object
    segments = seg.SegmentsHandler(access_token,'data')
    segments.sync()