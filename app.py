import os
from flask import Flask, request, jsonify
from requests import Response
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_info(playlist_id):
    playlist_data = sp.playlist(playlist_id)
    playlist_cover = playlist_data['images'][0]['url']
    tracks = []

    for item in playlist_data['tracks']['items']:
        track = item['track']
        track_name = track['name']
        track_url = track['external_urls']['spotify']
        track_cover = track['album']['images'][0]['url']
        
        tracks.append((track_name, track_url, track_cover))
    
    return playlist_data['name'], playlist_cover, tracks

@app.route('/')
def playlist_info():
    playlist_id = request.args.get('id')
    if not playlist_id:
        return "Error: No playlist ID provided", 400

    try:
        playlist_name, playlist_cover, tracks = get_playlist_info(playlist_id)
        
        output = f"Playlist: {playlist_name}\n"
        output += f"Playlist Cover: {playlist_cover}\n\n"
        output += "Tracks:\n"
        
        for i, (name, url, cover) in enumerate(tracks, 1):
            output += f"{i}. {name}\n"
            output += f"   Link: <a href='{url}'>{url}</a>\n"
            output += f"   Cover: <a href='{cover}'>{cover}</a>\n\n"

        return Response(output, mimetype='text/plain')
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)