import os
import pprint
from flask import Flask, request, jsonify, Response
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_info(playlist_id):
    playlist_data = sp.playlist(playlist_id)
    playlist_uri = playlist_data['uri']
    playlist_cover = playlist_data['images'][0]['url']
    tracks = []

    for item in playlist_data['tracks']['items']:
        track = item['track']
        track_name = track['name']
        track_url = track['external_urls']['spotify']
        track_cover = track['album']['images'][0]['url']
        
        tracks.append((track_name, track_url, track_cover))
    
    return playlist_data['name'], playlist_uri, playlist_cover, tracks


@app.route('/')
def playlist_info():
    playlist_id = request.args.get('id')
    if not playlist_id:
        return "Error: No playlist ID provided", 400

    try:
        playlist_name, playlist_uri, playlist_cover, tracks = get_playlist_info(playlist_id)
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Playlist</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .playlist-cover {{ width: 200px; }}
        .track {{ padding: 10px; }}
        .track-cover {{ width: 100px; }}
    </style>
</head>
<body>
    <h1>Playlist: <a href="{playlist_uri}">{playlist_name}</a></h1>
    <img src="{playlist_cover}" alt="Playlist Cover" class="playlist-cover"><br><br>
    <h2>Tracks:</h2>
    <ol>
        {tracks_html}
    </ol>
</body>
</html>
"""
        
        tracks_html = ""
        for name, url, cover in tracks:
            tracks_html += f"<li class='track'><strong>{name}</strong><br>"
            tracks_html += f"<a href='{url}'>{url}</a><br>"
            tracks_html += f"<img src='{cover}' alt='Track Cover' class='track-cover'></li>"
        
        output = html_template.format(
            playlist_name=playlist_name,
            playlist_uri=playlist_uri,
            playlist_cover=playlist_cover,
            tracks_html=tracks_html
        )
        
        return Response(output, mimetype='text/html')
    except Exception as e:
        pprint(e)
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)