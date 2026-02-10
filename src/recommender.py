import torch
import pandas as pd

SEARCH_LIMIT = 20
REC_LIMIT = 100
MAX_POOL = 300

class Recommender:
    def __init__(self, data):
        self.data = data.copy()

        # Audio features
        self.feature_cols = [
            'danceability_norm',
            'energy_norm',
            'valence_norm',
            'tempo_norm',
            'acousticness_norm',
            'instrumentalness_norm',
            'loudness_norm',
            'speechiness_norm',
            'mode_norm'
        ]

        # Optimization: Create search key for fast lookup
        self.data['search_key'] = (
            self.data['artist_name'].astype(str) + " " + self.data['track_name'].astype(str)
        ).str.lower()

    def search_song(self, query):
        if not query:
            return pd.DataFrame()

        query = query.lower().strip()

        # Fast string filtering
        mask = self.data['search_key'].str.contains(query, regex=False)
        results = self.data[mask]

        return results.sort_values(by='popularity', ascending=False).head(SEARCH_LIMIT)

    def recommend(self, user_features, selected_genre=None, limit=REC_LIMIT):
        # Genre filtering
        if selected_genre and selected_genre != "All Genres":
            target_data = self.data[self.data['genre'] == selected_genre]
        else:
            target_data = self.data

        if target_data.empty:
            return pd.DataFrame()

        # Prepare tensors
        data_array = target_data[self.feature_cols].values

        tensor_data = torch.tensor(data_array, dtype=torch.float32)
        user_tensor = torch.tensor([user_features], dtype=torch.float32)

        # Calculate Cosine Similarity
        similarity = torch.nn.functional.cosine_similarity(user_tensor, tensor_data)

        # Select top candidates
        pool_size = min(len(target_data), max(MAX_POOL, limit))
        _, indices = torch.topk(similarity, pool_size)

        candidates = target_data.iloc[indices.numpy()]

        # Hybrid Sort (Popularity)
        candidates = candidates.sort_values(by='popularity', ascending=False)

        return candidates.head(limit)