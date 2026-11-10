import os
import sys
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_DIR)

from src.data_loader import DataLoader, find_dataset
from src.recommender import Recommender
from src import ai_tools

mcp = MCPServer(
    "ai-music-recommender",
    instructions=(
        "Music recommender with about 1 million Spotify tracks. "
        "Translate the user's request (mood, activity, similar artist) into audio features "
        "and use the tools to find tracks. Always show artist and track name."
    )
)

# Data is loaded once, on the first tool call
engine = None
genres = []


def get_engine():
    """Loads the dataset and creates the Recommender (only the first time)."""
    global engine, genres
    if engine is None:
        file_path = find_dataset(os.path.join(PROJECT_DIR, "data"))
        # ToolError messages are shown to the AI, other errors are hidden
        if file_path is None:
            raise ToolError("Dataset not found. Put spotify_data.csv from Kaggle in the data folder.")

        loader = DataLoader(file_path)
        engine = Recommender(loader.prepare_data())
        genres = loader.get_genres()
    return engine


@mcp.tool()
def search_tracks(query: str, limit: int = 10) -> list[dict]:
    """Search tracks by artist and/or track name, e.g. 'rihanna stay'.
    Use it to find the track_id of a song the user mentions."""
    return ai_tools.search_tracks(get_engine(), query, limit)


@mcp.tool()
def recommend_by_features(
        danceability: float = 0.5,
        energy: float = 0.5,
        valence: float = 0.5,
        tempo: float = 0.5,
        acousticness: float = 0.5,
        instrumentalness: float = 0.0,
        loudness: float = 0.7,
        speechiness: float = 0.05,
        mode: int = 1,
        genre: str | None = None,
        limit: int = 10
) -> list[dict]:
    """Recommend tracks that match audio features. All features are numbers from 0 to 1:
    danceability (how danceable), energy (calm 0 - intense 1), valence (sad 0 - happy 1),
    tempo (slow 0 - fast 1), acousticness, instrumentalness (1 = no vocals),
    loudness (quiet 0 - loud 1), speechiness (spoken words), mode (1 = major, 0 = minor).
    Example: calm music for studying -> energy 0.2, instrumentalness 0.8, valence 0.5.
    genre is optional, use list_genres for valid names."""
    get_engine()
    try:
        return ai_tools.recommend_by_features(
            engine, genres, danceability, energy, valence, tempo, acousticness,
            instrumentalness, loudness, speechiness, mode, genre, limit
        )
    except ValueError as e:
        raise ToolError(str(e))


@mcp.tool()
def recommend_similar(track_id: str, limit: int = 10, same_genre: bool = True) -> list[dict]:
    """Recommend tracks that sound similar to a track. Get the track_id from search_tracks."""
    try:
        return ai_tools.recommend_similar(get_engine(), track_id, limit, same_genre)
    except ValueError as e:
        raise ToolError(str(e))


@mcp.tool()
def list_genres() -> list[str]:
    """List all genres available in the dataset."""
    get_engine()
    return genres


if __name__ == "__main__":
    mcp.run()
