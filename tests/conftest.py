import numpy as np
import pandas as pd
import pytest

from src.data_loader import DataLoader
from src.recommender import Recommender

COLUMNS = [
    'artist_name', 'track_name', 'track_id', 'popularity', 'year', 'genre',
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'duration_ms', 'time_signature'
]

# Small fake dataset with the same columns as the Kaggle file
TRACKS = [
    # artist, track, id, popularity, year, genre, dance, energy, key, loudness, mode, speech, acoustic, instr, live, valence, tempo
    ['Calm Artist', 'Quiet Piano', 'calm1', 50, 2015, 'ambient', 0.20, 0.10, 0, -25.0, 1, 0.03, 0.90, 0.90, 0.1, 0.40, 70.0],
    ['Calm Artist', 'Soft Rain', 'calm2', 40, 2016, 'ambient', 0.25, 0.15, 2, -23.0, 1, 0.03, 0.85, 0.85, 0.1, 0.45, 75.0],
    ['Party Band', 'Dance All Night', 'party1', 80, 2020, 'dance', 0.90, 0.90, 5, -4.0, 1, 0.05, 0.05, 0.00, 0.2, 0.90, 128.0],
    ['Party Band', 'Club Lights', 'party2', 70, 2021, 'dance', 0.85, 0.85, 7, -5.0, 1, 0.06, 0.10, 0.00, 0.2, 0.85, 124.0],
    ['Sad Singer', 'Rainy Day', 'sad1', 60, 2018, 'acoustic', 0.30, 0.20, 9, -15.0, 0, 0.04, 0.80, 0.00, 0.1, 0.10, 80.0],
    # Duplicate of 'Dance All Night' with lower popularity - should be removed
    ['Party Band', 'Dance All Night', 'party1_old', 10, 2019, 'dance', 0.90, 0.90, 5, -4.0, 1, 0.05, 0.05, 0.00, 0.2, 0.90, 128.0],
    # Missing energy - should be removed
    ['Broken', 'No Energy', 'broken1', 5, 2010, 'ambient', 0.50, np.nan, 1, -10.0, 1, 0.05, 0.50, 0.50, 0.1, 0.50, 100.0],
    # Missing artist name - should become 'Unknown'
    [np.nan, 'Mystery Song', 'mystery1', 30, 2012, 'acoustic', 0.40, 0.40, 3, -12.0, 0, 0.05, 0.60, 0.10, 0.1, 0.50, 95.0],
]


def make_raw_data():
    # Add duration_ms and time_signature to every track
    rows = [track + [200000, 4] for track in TRACKS]
    return pd.DataFrame(rows, columns=COLUMNS)


@pytest.fixture
def raw_data():
    return make_raw_data()


@pytest.fixture
def loader(raw_data):
    loader = DataLoader("unused.parquet")
    loader.prepare_data(raw_data)
    return loader


@pytest.fixture
def engine(loader):
    return Recommender(loader.data)


@pytest.fixture
def genres(loader):
    return loader.get_genres()
