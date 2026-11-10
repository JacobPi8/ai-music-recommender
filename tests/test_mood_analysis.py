from src.mood_analysis import get_mood_label, denormalize, format_key_mode


def test_party_track_with_fast_tempo():
    # valence, energy, danceability, acousticness, loudness (dB), tempo (BPM)
    mood = get_mood_label(0.8, 0.75, 0.85, 0.1, -5.0, 140.0)
    assert mood == "Upbeat Party / Festival"


def test_party_track_with_slow_tempo():
    mood = get_mood_label(0.8, 0.75, 0.85, 0.1, -5.0, 100.0)
    assert mood == "Feel Good / Sunny Vibes"


def test_calm_ambient_track():
    mood = get_mood_label(0.5, 0.2, 0.3, 0.3, -20.0, 110.0, instrumentalness=0.9)
    assert mood == "Focus / Ambient / Study"


def test_sad_acoustic_track():
    mood = get_mood_label(0.2, 0.3, 0.4, 0.8, -15.0, 80.0)
    assert mood == "Melancholic / Sad Acoustic"


def test_denormalize():
    assert denormalize(0.0, (60.0, 180.0)) == 60.0
    assert denormalize(0.5, (60.0, 180.0)) == 120.0
    assert denormalize(1.0, (-60.0, 0.0)) == 0.0


def test_slider_values_are_converted_before_mood_analysis():
    # Regression test: sliders give 0-1 values, the mood needs BPM and dB.
    # A fast tempo slider (0.9) must give a fast tempo mood.
    tempo_bpm = denormalize(0.9, (60.0, 180.0))
    loudness_db = denormalize(0.9, (-60.0, 0.0))
    mood = get_mood_label(0.8, 0.75, 0.85, 0.1, loudness_db, tempo_bpm)
    assert mood == "Upbeat Party / Festival"


def test_format_key_mode():
    assert format_key_mode(0, 1) == "C Major"
    assert format_key_mode(9, 0) == "A Minor"
    assert format_key_mode(12, 1) == "Unknown"
    assert format_key_mode(None, 1) == "Unknown"
