import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Supported dataset files (first one found is used)
DATASET_FILES = ["dataset.parquet", "spotify_data.csv"]


def find_dataset(data_folder):
    """Returns the path of the first dataset file found in the data folder."""
    for file_name in DATASET_FILES:
        file_path = os.path.join(data_folder, file_name)
        if os.path.exists(file_path):
            return file_path
    return None


class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

        # Audio features to normalize
        self.feature_columns = [
            'danceability', 'energy', 'valence', 'tempo',
            'acousticness', 'instrumentalness', 'loudness',
            'speechiness', 'mode'
        ]

        # Real min/max of every feature (e.g. tempo in BPM, loudness in dB)
        self.feature_ranges = {}

    def load_file(self) -> pd.DataFrame:
        """Loads parquet or csv file."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if self.file_path.endswith(".csv"):
            return pd.read_csv(self.file_path, index_col=0)
        return pd.read_parquet(self.file_path)

    def prepare_data(self, data=None) -> pd.DataFrame:
        """Loads data, normalizes it, and removes duplicates."""
        # Load data (tests can pass a ready DataFrame)
        if data is None:
            self.data = self.load_file()
        else:
            self.data = data.copy()

        # Handle missing text values
        text_cols = ['artist_name', 'track_name']
        for col in text_cols:
            if col in self.data.columns:
                self.data[col] = self.data[col].fillna('Unknown').astype(str)

        # Verify all required raw columns exist
        missing_cols = [col for col in self.feature_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Missing required audio columns: {missing_cols}")

        # Normalize audio features (0-1 range)
        self.data = self.data.dropna(subset=self.feature_columns)

        for col in self.feature_columns:
            self.feature_ranges[col] = (float(self.data[col].min()), float(self.data[col].max()))

        scaler = MinMaxScaler()
        norm_cols = [f"{col}_norm" for col in self.feature_columns]
        self.data[norm_cols] = scaler.fit_transform(self.data[self.feature_columns])

        # Delete duplicates - keep the most popular version
        if 'popularity' in self.data.columns:
            self.data = self.data.sort_values(by='popularity', ascending=False)

        self.data = self.data.drop_duplicates(subset=['artist_name', 'track_name'], keep='first')

        return self.data

    def get_genres(self) -> list:
        """Returns a sorted list of unique genres."""
        if self.data is None or 'genre' not in self.data.columns:
            return []

        genres = self.data['genre'].dropna().unique().tolist()
        # Filter short/invalid names
        return sorted([str(g) for g in genres if len(str(g)) > 2])
