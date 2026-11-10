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

        # Optimization: Create the feature tensor once (not on every search)
        self.tensor_data = torch.tensor(self.data[self.feature_cols].values, dtype=torch.float32)

    def search_song(self, query, limit=SEARCH_LIMIT):
        if not query:
            return pd.DataFrame()

        query = query.lower().strip()

        # Fast string filtering
        mask = self.data['search_key'].str.contains(query, regex=False)
        results = self.data[mask]

        return results.sort_values(by='popularity', ascending=False).head(limit)

    def recommend(self, user_features, selected_genre=None, limit=REC_LIMIT):
        # Genre filtering
        if selected_genre and selected_genre != "All Genres":
            mask = (self.data['genre'] == selected_genre).values
            target_data = self.data[mask]
            tensor_data = self.tensor_data[torch.from_numpy(mask)]
        else:
            target_data = self.data
            tensor_data = self.tensor_data

        if target_data.empty:
            return pd.DataFrame()

        # Prepare tensors
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

    def similar_to_track(self, track_id, limit=REC_LIMIT, same_genre=True):
        """Recommends tracks with audio features similar to the given track."""
        found = self.data[self.data['track_id'] == track_id]
        if found.empty:
            return pd.DataFrame()

        track = found.iloc[0]
        user_features = track[self.feature_cols].astype(float).tolist()
        genre = track['genre'] if same_genre else None

        # Ask for one more track, because the track itself is usually in the results
        results = self.recommend(user_features, selected_genre=genre, limit=limit + 1)
        results = results[results['track_id'] != track_id]

        return results.head(limit)
