from spotipy.oauth2 import SpotifyClientCredentials
from jinja2 import Template
import webbrowser
import spotipy
import shutil
import random
import json
import re
import os


TOTAL_CARDS = 3
file_path = os.path.dirname(os.path.realpath(__file__))

def sanitize(track):
    """ Sanitize song names"""
    track = re.sub(r'\(.*?\)', '', track)  # Remove parentheses
    track = re.sub(r'([a-z])([A-Z])', '\g<1> \g<2>', track)
    track = re.sub(r'-.*', '', track)  # Remove dashes and after
    return track

if __name__ == '__main__':

    # Open config file
    with open('config.json', 'rt') as f:
        config = json.loads(f.read())

    # Get track list from spotify
    credentials = SpotifyClientCredentials(client_id=config['client_id'],
                                        client_secret=config['client_secret'])
    spotify = spotipy.Spotify(client_credentials_manager=credentials)
    results = spotify.playlist(config['playlist'])
    playlist = [t['track']['name'] for t in results['tracks']['items']]

    # Check playlist for duplicates
    if len(playlist) != len(set(playlist)):
        raise ValueError('Duplicate Song Found in Playlist')

    # Sanitize playlist and report results
    sanitized = list(map(sanitize, playlist))
    print('Sanitizations:')
    x = max([len(s) for s in sanitized])
    for sani, orig in zip(playlist, sanitized):    
        if orig != sani:
            print('  {:<{}} ← {}'.format(orig, x, sani))

    # Pad list with null so we can prototype
    if len(playlist) < 24:
        playlist += [''] * (24 - len(playlist))

    # Read template bingo card
    with open('template/bingo.html', 'rt') as f:
        template = Template(f.read())

    # Clean output folder
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.makedirs('output')

    for i in range(TOTAL_CARDS):
        with open('output/{}.html'.format(i+1), 'wt') as f:
            f.write(template.render(tracks=random.sample(sanitized, 24), num=i+1))
        #pdfkit.from_file('output/{}.html'.format(i+1), 'output/{}.pdf'.format(i+1))
        webbrowser.open('file://{}/output/{}.html'.format(file_path, i+1), new=2)
