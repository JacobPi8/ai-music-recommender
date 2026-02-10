def get_mood_label(
        valence,
        energy,
        danceability=0.5,
        acousticness=0.5,
        loudness=-18.0,
        tempo=100.0,
        instrumentalness=0.0,
        speechiness=0.1
) -> str:
    """Determines mood label based on audio features."""

    loud_norm = max(0.0, min(1.0, (loudness + 60) / 60))
    tempo_fast = tempo > 125
    tempo_mid = 90 < tempo <= 125
    tempo_slow = tempo <= 90

    # Extreme Intensity
    if energy > 0.82 or (energy > 0.76 and loud_norm > 0.88):
        if valence < 0.32:
            if tempo_slow:
                return "Doom / Heavy Sludge"
            return "Rage / Furious"
        if valence > 0.74:
            return "Euphoric / Hyper"
        return "Intense / Aggressive"

    # Party / Upbeat
    if danceability > 0.73 and energy > 0.63:
        if tempo_fast:
            if valence > 0.70:
                return "Upbeat Party / Festival"
            elif valence > 0.42:
                return "Groovy / Dancefloor"
            else:
                return "Dark Dance / Edgy Club"
        else:
            if valence > 0.72:
                return "Feel Good / Sunny Vibes"
            elif valence > 0.48:
                return "Playful / Bouncy"
            else:
                return "Trippy / Psychedelic Groove"

    # Motivational / Empowering
    if 0.64 < energy <= 0.82 and valence > 0.56:
        if danceability > 0.60:
            return "Empowering / Confident"
        else:
            return "Motivational / Driven"

    # Happy / Uplifting
    if valence > 0.72:
        if energy < 0.58 and acousticness > 0.48:
            return "Hopeful / Heartwarming"
        if energy < 0.42:
            return "Dreamy Happy"
        if energy > 0.70:
            return "Uplifting / Euphoric Pop"
        return "Happy / Bright"

    # Romantic / Intimate
    if 0.42 <= valence <= 0.74 and energy < 0.64:
        if tempo_slow and acousticness > 0.4:
            return "Slow Dance / Ballad"
        if danceability > 0.66 and tempo_mid:
            return "Sensual / Seductive"
        if acousticness > 0.62 or (energy < 0.48 and valence > 0.50):
            return "Romantic / Intimate"
        if valence > 0.58:
            return "Warm / Tender"

    # Sad / Dark
    if valence < 0.38:
        if energy < 0.42:
            if tempo_slow and instrumentalness > 0.6:
                return "Solemn / Mournful"
            if acousticness > 0.68:
                return "Melancholic / Sad Acoustic"
            if instrumentalness > 0.55:
                return "Lonely / Reflective"
            if speechiness > 0.20:
                return "Depressing / Heavy-hearted"
            return "Desolate / Empty"
        else:
            if tempo_fast:
                return "Angry / Frantic"
            if energy > 0.70:
                return "Dark / Brooding"
            return "Sad / Angsty"

    # Chill / Relaxed
    if energy < 0.48:
        if acousticness > 0.72:
            if valence > 0.62:
                return "Cozy / Warm"
            elif valence > 0.32:
                return "Calm / Healing"
            else:
                return "Bittersweet Chill"
        if instrumentalness > 0.78:
            if tempo_slow:
                return "Deep Ambient / Drone"
            return "Focus / Ambient / Study"
        if valence > 0.54:
            return "Relaxed / Mellow"
        return "Chill / Downtempo"

    # Atmospheric / Dreamy
    if instrumentalness > 0.65 and (energy > 0.52 or loud_norm > 0.70):
        return "Epic / Cinematic"
    if instrumentalness > 0.50 and energy < 0.52 and valence > 0.44:
        return "Dreamy / Ethereal"
    if 0.40 <= valence <= 0.64 and acousticness > 0.58:
        return "Nostalgic / Reflective"

    # Gloomy / Moody
    if valence < 0.50 and energy < 0.54:
        return "Gloomy / Dreary"
    if 0.42 < valence < 0.66:
        if energy > 0.60:
            return "Bittersweet / Mixed Emotions"
        else:
            return "Moody / Contemplative"

    # Neutral
    return "Balanced / Neutral Vibe"


def format_key_mode(key, mode) -> str:
    """Converts numeric key and mode to string."""
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    try:
        key_int = int(key)
        if 0 <= key_int < len(keys):
            key_note = keys[key_int]
        else:
            return "Unknown"
    except (ValueError, TypeError):
        return "Unknown"

    mode_str = "Major" if mode == 1 else "Minor" if mode == 0 else "?"
    return f"{key_note} {mode_str}"