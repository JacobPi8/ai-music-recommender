import json

import pytest

from src import ai_tools


def test_search_tracks_returns_simple_dicts(engine):
    tracks = ai_tools.search_tracks(engine, "quiet piano")

    assert len(tracks) == 1
    track = tracks[0]
    assert track['artist'] == 'Calm Artist'
    assert track['track'] == 'Quiet Piano'
    assert track['track_id'] == 'calm1'
    assert track['tempo_bpm'] == 70
    assert track['key'] == 'C Major'
    assert isinstance(track['mood'], str)


def test_results_can_be_sent_as_json(engine, genres):
    tracks = ai_tools.recommend_by_features(engine, genres)
    json.dumps(tracks)


def test_search_limit_is_clamped(engine):
    assert len(ai_tools.search_tracks(engine, "a", limit=0)) == 1
    assert len(ai_tools.search_tracks(engine, "a", limit=1000)) <= ai_tools.MAX_RESULTS


def test_recommend_by_features_with_genre(engine, genres):
    tracks = ai_tools.recommend_by_features(engine, genres, energy=0.9, genre='dance')
    assert {track['genre'] for track in tracks} == {'dance'}


def test_recommend_by_features_unknown_genre(engine, genres):
    with pytest.raises(ValueError, match="list_genres"):
        ai_tools.recommend_by_features(engine, genres, genre='polka')


def test_recommend_by_features_clamps_values(engine, genres):
    # Values outside 0-1 must not crash the search
    tracks = ai_tools.recommend_by_features(engine, genres, energy=5, valence=-3, limit=2)
    assert len(tracks) == 2


def test_recommend_similar(engine):
    tracks = ai_tools.recommend_similar(engine, 'party1')
    assert 'party1' not in [track['track_id'] for track in tracks]


def test_recommend_similar_unknown_track(engine):
    with pytest.raises(ValueError, match="search_tracks"):
        ai_tools.recommend_similar(engine, 'missing')
