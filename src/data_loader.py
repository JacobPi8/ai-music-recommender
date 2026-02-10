import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


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

    def prepare_data(self) -> pd.DataFrame:
        """Loads parquet file, normalizes data, and removes duplicates."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Load data
        self.data = pd.read_parquet(self.file_path)

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