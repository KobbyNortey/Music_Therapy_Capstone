from uuid import uuid4
import requests
import random


class PlaylistManager:
    def __init__(self, access_token):
        self.access_token = access_token
        self.spotify_api_base_url = 'https://api.spotify.com/v1/'
        self.mood_genre_mapping = {
            'happy': ['pop', 'dance', 'funk', 'disco'],
            'sad': ['blues', 'acoustic', 'classical', 'singer-songwriter'],
            'energetic': ['rock', 'hip-hop', 'edm', 'metal'],
            'calm': ['ambient', 'chill', 'acoustic', 'jazz'],
            'romantic': ['r&b', 'soul', 'ballads', 'latin'],
            'reflective': ['indie', 'folk', 'alternative', 'classical'],
            'angry': ['punk', 'hard rock', 'metal', 'rap'],
            'uplifted': ['reggae', 'ska', 'gospel', 'world music']
        }

    def determine_therapy_type(self, current_mood, goal_mood):
        """Determines the ideal therapy genres based on user's current mood and desired state."""
        # Map of ideal moods for therapy
        ideal_mood_mapping = {
            'tired': 'energetic',
            'stressed': 'calm',
            'sad': 'happy',
            'angry': 'calm',
            'bored': 'uplifted',
            'anxious': 'relaxed'
        }

        # Determine the ideal mood if the goal mood is not directly provided
        ideal_mood = ideal_mood_mapping.get(current_mood.lower(), goal_mood.lower())

        # Return the corresponding genres for the ideal mood
        return self.mood_genre_mapping.get(ideal_mood, ['pop'])

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

    def curate_playlist(self, user_id, current_mood, goal_mood):
        """Creates a Spotify playlist for the specified therapy type."""
        genres = self.determine_therapy_type(current_mood, goal_mood)

        playlist_name = "Therapy - " + str(uuid4())[:8] + f" {current_mood} to {goal_mood}"
        playlist = self.create_playlist(user_id, playlist_name)

        track_uris = []

        for genre in genres:
            results = self.search_tracks(f'genre:{genre}')
            if results:
                track_uris += [item['uri'] for item in results]

        if track_uris:
            self.add_songs_to_playlist(playlist['id'], track_uris[:30])  # Limit to 30 tracks
        return playlist_name, playlist['external_urls']['spotify']



