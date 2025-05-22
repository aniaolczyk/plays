"""
Prerequisites

    pip3 install spotipy Flask Flask-Session

    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID="5a7259409c1d48dd8497ff52f0786e5a"
    export SPOTIPY_CLIENT_SECRET="3791625e9fa74e279eeb2876a396bf3f"
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:5000/' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py

    // on Windows, use `SET` instead of `export`

Run app.py

    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

# TODO
# start a server with this app running
# in the server, there should be 
# One way(more work) is to implement multiple session using https://github.com/pallets-eco/flask-session
# Another is to run 6 instances of this, and Add /plays endpoint that will refresh and do next() every 40 seconds.

#
# Konfiguracja
# Idziemy do plays.onrender.com
# Logujemy się do spotify i dajemy permissions
# Odtwarzamy cos na telefonie
# Patrzymy czy zmienia.
# /random tworzy ALT Playlisty
#

import jinja2
import os
from flask import Flask, session, request, redirect, copy_current_request_context, render_template
from flask_session import Session
import spotipy
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = '10000'
Session(app)

##################
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials


client_id = os.environ.get("SPOTIPY_CLIENT_ID")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")

ania_uri = 'spotify:artist:1AfgDOc4Q0Z7LZpdQbU49y'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# results = spotify.artist_albums(birdy_uri, album_type='album')
# albums = results['items']
# while results['next']:
#     results = spotify.next(results)
#     albums.extend(results['items'])

# for album in albums:
#     print(album['name'])

def mix(songs, ania_songs, n):
    logging.warn(f"mixing {len(songs)}, {len(ania_songs)}, n={n}")
    result = []
    for i in range(len(songs)//n):
        result.extend(songs[n*i: n*(i+1)] + ania_songs)
    return result

def get_playlist_items_uris(playlist_id):
    return_list = []
    results = spotify.playlist_items(playlist_id)
    for track in results["items"]:
        return_list.append(track["track"]["uri"])
    return return_list

def get_artists_singles(uri):
    return_list = []
    results = spotify.artist_albums(uri)
    for i in results['items']:
        return_list.append(i['uri'])
    return return_list

def get_user_playlist(client: spotipy.Spotify):
    playlists = client.current_user_playlists()
    for p in playlists:
        if "Ania Olczyk" in p["name"]:
            return p["uri"]


# ania_uris = get_artists_singles(ania_uri)
ania_uris = ['spotify:track:3g87eKym3fy8V4R6SRwX4o', 'spotify:track:422Uq4fEQTN7yKTgAIT1r0', 'spotify:track:4ceFqwXDVpeswyYMHL1g06']
#####
alt_id = '4KbJ2Zd2Cy7xRXBBrfNGL5'
alt_uris = get_playlist_items_uris("4KbJ2Zd2Cy7xRXBBrfNGL5")

# print(ania_uris)
# print(alt_uris)
user_id = "1166760170"
#####

def create_playlist_with_tracks(sp, user_id, name, track_uris):
    playlist = sp.user_playlist_create(user_id, name, public=False, collaborative=False)
    pid = playlist["id"]
    sp.user_playlist_add_tracks(user_id, pid, track_uris)
    return playlist
#4KbJ2Zd2Cy7xRXBBrfNGL5
def create_random_ania_alt_playlist_with_tracks(sp, name):
    ania_uris = ['spotify:track:3g87eKym3fy8V4R6SRwX4o', 'spotify:track:422Uq4fEQTN7yKTgAIT1r0', 'spotify:track:3g87eKym3fy8V4R6SRwX4o', 'spotify:track:4ceFqwXDVpeswyYMHL1g06', 'spotify:track:3g87eKym3fy8V4R6SRwX4o']
    alt_uris = get_playlist_items_uris(alt_id)
    user_id = sp.me()["id"]
    # playlist = create_playlist_with_tracks(sp, user_id, name, alt_uris[:5] + ania_uris + ania_uris)
    playlist = create_playlist_with_tracks(sp, user_id, name, mix(random.sample(alt_uris, 20), ania_uris, 3))
    return playlist

# user_auth(scope, user_id)
# create_playlist_with_tracks(user_id, "Test", alt_uris[:5] + ania_uris)
###############
@app.route('/')
def index():
    logging.warn("opened")
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-public playlist-modify-private user-modify-playback-state user-read-playback-state',
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Zaloguj</a></h2>'

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return  render_template('index.html', user_name=spotify.me()["display_name"])
    # return f'<h2>Hi {spotify.me()["display_name"]}, ' \
    #        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
    #        f'<a href="/playlists">my playlists</a> | ' \
    #        f'<a href="/currently_playing">currently playing</a> | ' \
    #     f'<a href="/current_user">me</a>' \



@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


# @app.route('/clear_playlists')
# def clear_playlists():
#     cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
#     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
#     if not auth_manager.validate_token(cache_handler.get_cached_token()):
#         return redirect('/')

#     spotify = spotipy.Spotify(auth_manager=auth_manager)
#     playlists = spotify.user_playlists()
#     count = 0
#     for p in playlists:
#         if "Ania Olczyk" in p["name"]:
#             spotify.
#     return spotify.current_user_playlists()

@app.route('/random')
def random_():
    ania_uris = ['spotify:track:3g87eKym3fy8V4R6SRwX4o', 'spotify:track:422Uq4fEQTN7yKTgAIT1r0', 'spotify:track:3g87eKym3fy8V4R6SRwX4o', 'spotify:track:4ceFqwXDVpeswyYMHL1g06', 'spotify:track:3g87eKym3fy8V4R6SRwX4o',]
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    for i in range(6):
        p = create_playlist_with_tracks(spotify, user_id, f"Alt PL #{i+1}", mix(alt_uris[i*10:(i+1)*10+1], ania_uris, len(ania_uris)))
    return p



##### THREAD LOGGING #####
import threading
import logging
import logging.config


class ThreadLogFilter(logging.Filter):
    """
    This filter only show log entries for specified thread name
    """

    def __init__(self, thread_name, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.thread_name = thread_name

    def filter(self, record):
        return record.threadName == self.thread_name


def start_thread_logging():
    """
    Add a log handler to separate file for current thread
    """
    thread_name = threading.current_thread().getName()
    log_file = '/tmp/perThreadLogging-{}.log'.format(thread_name)
    log_handler = logging.FileHandler(log_file)

    log_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)-15s"
        "| %(threadName)-11s"
        "| %(levelname)-5s"
        "| %(message)s")
    log_handler.setFormatter(formatter)

    log_filter = ThreadLogFilter(thread_name)
    log_handler.addFilter(log_filter)

    logger = logging.getLogger()
    logger.addHandler(log_handler)

    return log_handler


def stop_thread_logging(log_handler):
    # Remove thread log handler from root logger
    logging.getLogger().removeHandler(log_handler)

    # Close the thread log handler so that the lock on log file can be released
    log_handler.close()


def config_root_logger():
    log_file = '/tmp/perThreadLogging.log'

    formatter = "%(asctime)-15s" \
                "| %(threadName)-11s" \
                "| %(levelname)-5s" \
                "| %(message)s"

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'root_formatter': {
                'format': formatter
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'root_formatter'
            },
            'log_file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'filename': log_file,
                'formatter': 'root_formatter',
            }
        },
        'loggers': {
            '': {
                'handlers': [
                    'console',
                    'log_file',
                ],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    })

##### THREAD LOGGING ##### 
stop_thread = {}
@app.route('/plays')
def plays():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user_name = spotify.me()["display_name"]
    current_device_id = spotify.devices()["devices"][0]["id"]
    # TODO check if playlist exists
    playlist = get_user_playlist(spotify)
    if not playlist:
        playlist = create_random_ania_alt_playlist_with_tracks(spotify, f"Ania dla {user_name}")
    spotify.start_playback(device_id=current_device_id, context_uri=playlist["uri"])
    spotify.repeat("context")
    spotify.user_playlist_change_details(spotify.me()["id"], playlist["id"], public=False)
    @copy_current_request_context
    def worker(client, stop):
        thread_log_handler = start_thread_logging()
        thread_log_handler.setLevel("INFO")
        logging.info('Info log entry in sub thread.')
        # TODO ADD starting playing the playlist and set looping correctly
        while True:
            if stop():
                logging.warning("received stop, bye.")
                break
            logging.warning("playing next: " + str(spotify.current_user()))
            resp = spotify.current_user_playing_track()
            logging.info("resp", resp)
            success = False
            devices = spotify.devices()["devices"]
            if len(devices):
                current_device_id = devices[0]["id"]
            else:
                logging.warning("no device found user: " + str(spotify.current_user()))
                continue
            try:
                
                if resp['item']['album']['artists'][0]['uri'] != ania_uri:
                    client.next_track()
                    success = True
            except:
                logging.info("error: " + str(resp))
            if not success:
                client.next_track()
            time.sleep(35)
        stop_thread_logging(thread_log_handler)
    thread_name = 'Thread-{}'.format(user_name)
    global stop_thread
    stop_thread[thread_name] = False
    t = threading.Thread(
        target=worker,
        name=thread_name,
        args=[spotify, lambda: stop_thread[thread_name]]
    )
    t.start()
    return render_template('index.html', user_name=spotify.me()["display_name"], message="Dzięki, leci ;)")


@app.route('/stop')
def stop():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user_name = spotify.me()["display_name"]
    global stop_thread
    thread_name = 'Thread-{}'.format(user_name)
    stop_thread[thread_name] = True
    return redirect("/")

@app.route('/next')
def next():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    a = spotify.next_track()
    return a

@app.route('/next_check')
def next_check():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    resp = spotify.current_user_playing_track()
    logging.info("resp", resp)
    success = False
    a = ''
    try:
        if resp['item']['album']['artists'][0]['uri'] != ania_uri:
            a = spotify.next_track()
            success = True
    except:
        logging.info("error", resp)
    if not success:
        a = spotify.next_track()
    return a


@app.route('/me')
def me():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.me()

@app.route('/devices')
def devices():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.devices()

@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    config_root_logger()
    app.run(threaded=True, port=int(
        os.environ.get("PORT", os.environ.get("SPOTIPY_REDIRECT_URI", 5000).split(":")[-1].replace("/", "")))
    )