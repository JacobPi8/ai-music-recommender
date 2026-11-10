from src.mood_analysis import get_mood_label, format_key_mode

MAX_RESULTS = 50


def track_info(row) -> dict:
    """Converts one dataset row to a simple dict that the AI can read."""
    return {
        'track_id': row['track_id'],
        'artist': row['artist_name'],
        'track': row['track_name'],
        'genre': row.get('genre', None),
        'year': int(row['year']) if 'year' in row else None,
        'popularity': int(row['popularity']),
        'mood': get_mood_label(
            row['valence'], row['energy'], row['danceability'], row['acousticness'],
            row['loudness'], row['tempo'], row['instrumentalness'], row['speechiness']
        ),
        'key': format_key_mode(row['key'], row['mode']) if 'key' in row else None,
        'tempo_bpm': round(float(row['tempo'])),
    }


def to_track_list(results) -> list:
    """Converts a DataFrame with tracks to a list of dicts."""
    return [track_info(row) for _, row in results.iterrows()]


def clamp(value, low, high):
    """Keeps a value inside the given range."""
    return max(low, min(high, value))


def search_tracks(engine, query, limit=10) -> list:
    """Finds tracks by artist and/or track name."""
    limit = clamp(limit, 1, MAX_RESULTS)
    return to_track_list(engine.search_song(query, limit=limit))


def recommend_by_features(engine, genres, danceability=0.5, energy=0.5, valence=0.5,
                          tempo=0.5, acousticness=0.5, instrumentalness=0.0,
                          loudness=0.7, speechiness=0.05, mode=1, genre=None, limit=10) -> list:
    """Recommends tracks matching the given audio features (all values 0-1)."""
    if genre and genre not in genres:
        raise ValueError(f"Unknown genre: '{genre}'. Use list_genres to see available genres.")

    # Same order as the sliders in main.py
    user_vector = [
        clamp(danceability, 0, 1), clamp(energy, 0, 1), clamp(valence, 0, 1),
        clamp(tempo, 0, 1), clamp(acousticness, 0, 1), clamp(instrumentalness, 0, 1),
        clamp(loudness, 0, 1), clamp(speechiness, 0, 1), 1 if mode else 0
    ]
    limit = clamp(limit, 1, MAX_RESULTS)
    return to_track_list(engine.recommend(user_vector, selected_genre=genre, limit=limit))


def recommend_similar(engine, track_id, limit=10, same_genre=True) -> list:
    """Recommends tracks similar to the track with the given track_id."""
    limit = clamp(limit, 1, MAX_RESULTS)
    results = engine.similar_to_track(track_id, limit=limit, same_genre=same_genre)
    if results.empty:
        raise ValueError(f"Track not found: '{track_id}'. Use search_tracks to find the track_id.")
    return to_track_list(results)
