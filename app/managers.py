from uuid import uuid4
import requests
import random


class PlaylistManager:
    def __init__(self, access_token):
        self.access_token = access_token
        self.spotify_api_base_url = 'https://api.spotify.com/v1/'
        self.music_library = {
            'relaxation': ['ambient', 'nature sounds', 'calm'],
            'focus': ['concentration', 'focus music', 'study'],
            'energy': ['energetic', 'upbeat', 'workout', 'rap']
        }

    def determine_therapy_type(self, mood, goal):
        """Determines the therapy type based on user input."""

        if mood in ['tired', 'stressed', 'okay'] and goal in ['relaxation', 'focus', 'energy']:
            if mood == 'tired' or goal == 'relaxation':
                return 'relaxation'
            elif mood == 'stressed' or goal == 'focus':
                return 'focus'
            elif mood == 'okay' or goal == 'energy':
                return 'energy'

    def create_playlist(self, user_id, name, description=None, public=False):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        data = {
            'name': name,
            'public': public
        }
        if description:
            data['description'] = description
        response = requests.post(f'{self.spotify_api_base_url}users/{user_id}/playlists', headers=headers, json=data)
        return response.json() if response.status_code == 201 else None

    def add_songs_to_playlist(self, playlist_id, tracks):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        data = {
            'uris': tracks
        }
        response = requests.post(f'{self.spotify_api_base_url}playlists/{playlist_id}/tracks', headers=headers,
                                 json=data)
        return response.status_code == 201

    def search_tracks(self, query, limit=10):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'q': query, 'type': 'track', 'limit': limit}
        response = requests.get(f'{self.spotify_api_base_url}search', headers=headers, params=params)
        if response.status_code == 200:
            tracks = response.json().get('tracks', {}).get('items', [])
            random.shuffle(tracks)
            return tracks
        return []

    def curate_playlist(self, user_id, mood, goal):
        """Creates a Spotify playlist for the specified therapy type."""
        therapy_type = self.determine_therapy_type(mood, goal)

        playlist_name = "Therapy - " + str(uuid4())[:8] + f" {therapy_type}"
        playlist = self.create_playlist(user_id, playlist_name)

        search_keywords = self.music_library[therapy_type]
        track_uris = []

        for keyword in search_keywords:
            results = self.search_tracks(keyword)
            if results:
                track_uris += [item['uri'] for item in results]

        if track_uris:
            self.add_songs_to_playlist(playlist['id'], track_uris[:30])  # Limit to 10 tracks
        return playlist_name, playlist['external_urls']['spotify']
