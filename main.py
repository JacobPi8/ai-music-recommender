import os
import sys
import streamlit as st


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from src.data_loader import DataLoader
    from src.recommender import Recommender
    from src.mood_analysis import get_mood_label, format_key_mode
    from src.styles import APP_STYLES
except ImportError as e:
    st.error(f"Import Error: {e}. Make sure you are running the app from the root directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Music Recommender",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply CSS
st.markdown(APP_STYLES, unsafe_allow_html=True)


def init_session_state():
    """Sets default values for session state variables."""
    defaults = {
        'val_dance': 0.5, 'val_energy': 0.6, 'val_valence': 0.5,
        'val_acoustic': 0.1, 'val_instrumental': 0.0, 'val_speech': 0.05,
        'val_tempo': 0.5, 'val_loudness': 0.7, 'val_mode': 1,
        'search_results': None, 'page_offset': 0, 'current_mood': ""
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


@st.cache_resource
def initialize_system():
    """Loads data and initializes the Recommender engine."""
    if os.path.exists("data/dataset.parquet"):
        file_path = "data/dataset.parquet"
    elif os.path.exists("data/dataset2.csv"):
        file_path = "data/dataset2.csv"
    else:
        file_path = "data/dataset.csv"

    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        st.stop()

    loader = DataLoader(file_path)
    data = loader.prepare_data()
    engine = Recommender(data)
    genres = loader.get_genres()

    return engine, genres


def update_slider_values(row):
    """Updates session state sliders based on a selected track."""
    st.session_state.val_dance = float(row['danceability_norm'])
    st.session_state.val_energy = float(row['energy_norm'])
    st.session_state.val_valence = float(row['valence_norm'])
    st.session_state.val_acoustic = float(row['acousticness_norm'])
    st.session_state.val_instrumental = float(row['instrumentalness_norm'])
    st.session_state.val_speech = float(row['speechiness_norm'])
    st.session_state.val_tempo = float(row['tempo_norm'])
    st.session_state.val_loudness = float(row['loudness_norm'])
    st.session_state.val_mode = int(round(float(row['mode_norm'])))


# UI Rendering Functions

def render_header():
    st.title("🎧 AI Music Recommender")
    st.markdown(
        "<div style='color: #B3B3B3; margin-bottom: 25px;'>Select a genre or search for a track to match its vibe.</div>",
        unsafe_allow_html=True
    )


def render_search_section(engine):
    """Renders the song search expander."""
    with st.expander("Start from a favorite song (Copy Settings)"):
        col_s1, _ = st.columns([3, 1])
        with col_s1:
            song_query = st.text_input("Search for a track...", placeholder="e.g. Rihanna Stay")

        if song_query:
            found_tracks = engine.search_song(song_query)
            if not found_tracks.empty:
                found_tracks['display_label'] = found_tracks.apply(
                    lambda x: f"{x['artist_name']} - {x['track_name']}", axis=1
                )

                track_options = found_tracks['display_label'].tolist()
                selected_track_str = st.selectbox("Select specific track:", track_options)

                selected_row = found_tracks[found_tracks['display_label'] == selected_track_str].iloc[0]

                if st.button("APPLY AUDIO SETTINGS", key="apply_song"):
                    update_slider_values(selected_row)
                    st.toast(f"Settings updated to match '{selected_row['track_name']}'!")
                    st.rerun()
            else:
                st.warning("No tracks found.")


def render_sliders():
    """Renders the three columns of audio feature sliders."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Vibe")
        st.slider("Danceability", 0.0, 1.0, key="val_dance")
        st.slider("Energy", 0.0, 1.0, key="val_energy")
        st.slider("Happiness (Valence)", 0.0, 1.0, key="val_valence")
    with col2:
        st.subheader("Character")
        st.slider("Acousticness", 0.0, 1.0, key="val_acoustic")
        st.slider("Instrumentalness", 0.0, 1.0, key="val_instrumental")
        st.slider("Speechiness", 0.0, 1.0, key="val_speech")
    with col3:
        st.subheader("Tech Specs")
        st.slider("Tempo (Normalized)", 0.0, 1.0, key="val_tempo")
        st.slider("Loudness / Power", 0.0, 1.0, key="val_loudness")
        st.radio("Musical Mode", [0, 1], key="val_mode",
                 format_func=lambda x: "Minor" if x == 0 else "Major", horizontal=True)


def render_action_area(engine, selected_genre):
    """Renders mood display and the 'Find Tracks' button."""
    live_mood = get_mood_label(
        st.session_state.val_valence, st.session_state.val_energy, st.session_state.val_dance,
        st.session_state.val_acoustic, st.session_state.val_loudness, st.session_state.val_tempo,
        st.session_state.val_instrumental, st.session_state.val_speech
    )

    col_mood, col_btn = st.columns([3, 1], gap="medium")
    with col_mood:
        st.markdown(f"""
        <div class="mood-box">
            <span>Detected Mood:</span><span>{live_mood}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        if st.button("FIND TRACKS", use_container_width=True):
            user_vector = [
                st.session_state.val_dance, st.session_state.val_energy, st.session_state.val_valence,
                st.session_state.val_tempo, st.session_state.val_acoustic, st.session_state.val_instrumental,
                st.session_state.val_loudness, st.session_state.val_speech, st.session_state.val_mode
            ]
            results = engine.recommend(user_vector, selected_genre=selected_genre, limit=100)
            st.session_state.search_results = results
            st.session_state.page_offset = 0
            st.session_state.current_mood = live_mood


def render_results():
    """Renders the dataframe with batches."""
    if st.session_state.search_results is None:
        return

    results = st.session_state.search_results

    if results.empty:
        st.warning("No tracks found matching your criteria.")
        return

    start_idx = st.session_state.page_offset
    end_idx = start_idx + 20
    batch_data = results.iloc[start_idx:end_idx].copy()

    # Data formatting
    if 'key' in batch_data.columns and 'mode' in batch_data.columns:
        batch_data['Musical Key'] = batch_data.apply(
            lambda row: format_key_mode(row['key'], row['mode']), axis=1
        )
    else:
        batch_data['Musical Key'] = "N/A"

    cols_to_show = ['artist_name', 'track_name', 'genre', 'Musical Key']
    final_cols = [c for c in cols_to_show if c in batch_data.columns]

    rename_map = {
        'artist_name': 'Artist', 'track_name': 'Track Name',
        'genre': 'Genre', 'Musical Key': 'Key'
    }
    display_data = batch_data[final_cols].rename(columns=rename_map)

    # Header stats
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center;
                margin-top: 20px; margin-bottom: 10px; color: #B3B3B3; font-size: 14px;">
        <span>Found <b style="color: #FFB300">{len(results)}</b> tracks.</span>
        <span>Showing <b style="color: #FFB300">{start_idx + 1}-{min(end_idx, len(results))}</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        display_data,
        hide_index=True,
        use_container_width=True,
        height=720,
        column_config={
            "Artist": st.column_config.TextColumn("Artist", width="medium"),
            "Track Name": st.column_config.TextColumn("Track Name", width="large"),
            "Genre": st.column_config.TextColumn("Genre", width="small"),
            "Key": st.column_config.TextColumn("Key", width="small")
        }
    )

    # Batches Control
    if len(results) > end_idx:
        st.write("")
        if st.button("LOAD NEXT 20 TRACKS"):
            st.session_state.page_offset += 20
            st.rerun()


# Main Application

def main():
    init_session_state()
    render_header()

    try:
        engine, genres = initialize_system()
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        return

    # Search Section
    render_search_section(engine)

    # Genre Selection
    col_genre, _ = st.columns([1, 2])
    with col_genre:
        if not genres:
            genres = ["Pop", "Rock"]
        genre_options = ["All Genres"] + genres
        selected_genre = st.selectbox("Select Genre:", genre_options)

    st.markdown("---")

    # Sliders Section
    render_sliders()

    st.markdown("---")

    # Action Section
    render_action_area(engine, selected_genre)

    # Results Section
    render_results()

    # Footer
    st.markdown("<div class='footer'>© 2026 AI Music Recommender by Jakub Piotrowski</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()