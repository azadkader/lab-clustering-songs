from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QInputDialog, QListWidget, QListWidgetItem, QDialog
from PyQt5.QtCore import Qt
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import numpy as np
import pickle
from credentials import *
import os

# Load the scaler
with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

# Load the KMeans model
with open('kmeans7.pkl', 'rb') as file:
    model = pickle.load(file)

# Load the song data
df = pd.read_csv('extended_songs_clustered.csv')

# Create Spotify object
credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=credentials)

def search_song(title, artist, matches=10):
    """Search a song on Spotify and return its Spotify ID."""
    # Same as before...

def recommend_songs(title, artist):
    # Same as before...

    class SongRecommenderApp(QWidget):
        def __init__(self):
            super().__init__()

            self.title = 'Song Recommender'
            self.initUI()

            def initUI(self):
                self.setWindowTitle(self.title)

                layout = QVBoxLayout()

                self.label_song = QLabel('Enter a song title:')
                self.line_edit_song = QLineEdit()

                self.label_artist = QLabel('Enter the song artist:')
                self.line_edit_artist = QLineEdit()

                self.button = QPushButton('Recommend Songs')
                self.button.clicked.connect(self.on_click)

                layout.addWidget(self.label_song)
                layout.addWidget(self.line_edit_song)
                layout.addWidget(self.label_artist)
                layout.addWidget(self.line_edit_artist)
                layout.addWidget(self.button)

                self.setLayout(layout)

            def on_click(self):
                song = self.line_edit_song.text()
                artist = self.line_edit_artist.text()

                # Get song suggestions using the recommend_songs function from the recommendation script
                suggestions = recommend_songs(song, artist)

                # Create a new dialog to display the song suggestions
                dialog = SongSelectionDialog(suggestions)

                # If the user confirmed the selection, get the selected song and artist
                if dialog.exec_():
                    song_id, song, artist = dialog.selected_song

                # Fetch audio features, scale the features, predict the cluster, and get song recommendations
                audio_features = sp.audio_features([song_id])[0]
                song_df = pd.DataFrame([audio_features])

                # Define the features the scaler was trained on
                features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature', 'loudness', 'key', 'mode']

                # Only keep columns that the scaler was trained on
                song_df = song_df[features]

                # Scale the audio features and predict the cluster
                song_df_scaled = scaler.transform(song_df)

                # Convert scaled array back to DataFrame and assign original feature names
                song_df_scaled = pd.DataFrame(song_df_scaled, columns=features)

                # Predict the cluster
                cluster = model.predict(song_df_scaled)[0]

                # Check if the song is in our data and is 'hot'
                # The rest of the recommendation logic remains unchanged...

                # Select up to 5 recommendations
                recommendations = recommendations.sample(min(5, len(recommendations)))

                # Create a new dialog to display the song recommendations
                dialog = SongRecommendationsDialog(recommendations)
                dialog.exec_()


    class SongSelectionDialog(QDialog):
        def __init__(self, suggestions):
            super().__init__()

            self.setWindowTitle('Select a Song')

            layout = QVBoxLayout()

            self.list_widget = QListWidget()

            for song_id, song, artist in suggestions:
                item = QListWidgetItem(f'{song} by {artist}')
                item.setData(Qt.UserRole, (song_id, song, artist))  # Store song_id, song, and artist in the item data
                self.list_widget.addItem(item)

            self.list_widget.itemDoubleClicked.connect(self.accept)  # Accept the dialog when an item is double clicked

            layout.addWidget(self.list_widget)

            self.setLayout(layout)

        @property
        def selected_song(self):
            item = self.list_widget.currentItem()
            return item.data(Qt.UserRole)  # Return song_id, song, and artist of the selected item


    class SongRecommendationsDialog(QDialog):
        def __init__(self, recommendations):
            super().__init__()

            self.setWindowTitle('Song Recommendations')

            layout = QVBoxLayout()

            self.list_widget = QListWidget()

            for song, artist in recommendations:
                item = QListWidgetItem(f'{song} by {artist}')
                self.list_widget.addItem(item)

            layout.addWidget(self.list_widget)

            self.setLayout(layout)


    def main():
        app = QApplication([])

        window = SongRecommenderApp()
        window.show()

        app.exec_()


    if __name__ == '__main__':
        main()
