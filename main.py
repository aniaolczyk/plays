import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials


client_id = "5a7259409c1d48dd8497ff52f0786e5a"
client_secret = "3791625e9fa74e279eeb2876a396bf3f"

ania_uri = 'spotify:artist:1AfgDOc4Q0Z7LZpdQbU49y'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# results = spotify.artist_albums(birdy_uri, album_type='album')
# albums = results['items']
# while results['next']:
#     results = spotify.next(results)
#     albums.extend(results['items'])

# for album in albums:
#     print(album['name'])


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

ania_uris = get_artists_singles(ania_uri)
alt_top_uri="4KbJ2Zd2Cy7xRXBBrfNGL5"
x="6LUZL8RoQ3J2Ynn3MuPTyA"
alt_uris = get_playlist_items_uris(alt_top_uri)

print(ania_uris)
print(alt_uris)
user_id = "1166760170"


def create_playlist_with_tracks(user_id, name, track_uris):
    playlist = spotify.user_playlist_create(user_id, name)
    user_playlist_add_tracks(user_id, track_uris)
    print(playlist)
    return playlist

def create_random_playlists_with_tracks(track_uris, artist_uris):
    pass

# user_auth(scope, user_id)
create_playlist_with_tracks(user_id, "Test", alt_uris[:5] + ania_uris)