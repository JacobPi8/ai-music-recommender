from src import recommender

CALM_VECTOR = [0.2, 0.1, 0.4, 0.0, 0.9, 1.0, 0.0, 0.0, 1]


def test_search_is_case_insensitive(engine):
    results = engine.search_song("PARTY band")
    assert set(results['track_id']) == {'party1', 'party2'}


def test_search_sorts_by_popularity(engine):
    results = engine.search_song("party band")
    assert list(results['track_id']) == ['party1', 'party2']


def test_search_empty_query(engine):
    assert engine.search_song("").empty


def test_search_limit(engine):
    assert len(engine.search_song("a", limit=2)) == 2


def track_vector(engine, track_id):
    """Returns the normalized features of a track."""
    track = engine.data[engine.data['track_id'] == track_id].iloc[0]
    return track[engine.feature_cols].astype(float).tolist()


def test_recommend_most_similar_track(engine, monkeypatch):
    # With a pool of 1 only the most similar track is returned
    monkeypatch.setattr(recommender, "MAX_POOL", 1)

    for track_id in ['calm1', 'party1', 'sad1']:
        result = engine.recommend(track_vector(engine, track_id), limit=1)
        assert result.iloc[0]['track_id'] == track_id


def test_recommend_genre_filter(engine):
    results = engine.recommend(CALM_VECTOR, selected_genre='dance')
    assert set(results['genre']) == {'dance'}


def test_recommend_all_genres(engine):
    results = engine.recommend(CALM_VECTOR, selected_genre='All Genres')
    assert len(results) == len(engine.data)


def test_recommend_unknown_genre_is_empty(engine):
    assert engine.recommend(CALM_VECTOR, selected_genre='polka').empty


def test_recommend_limit(engine):
    assert len(engine.recommend(CALM_VECTOR, limit=3)) == 3


def test_similar_to_track_skips_the_track_itself(engine):
    results = engine.similar_to_track('calm1')
    assert 'calm1' not in results['track_id'].values
    assert set(results['genre']) == {'ambient'}


def test_similar_to_track_any_genre(engine):
    results = engine.similar_to_track('calm1', same_genre=False)
    assert 'calm1' not in results['track_id'].values
    assert len(results) == len(engine.data) - 1


def test_similar_to_unknown_track_is_empty(engine):
    assert engine.similar_to_track('missing').empty
