import anyio
import pytest
from mcp.server.mcpserver.exceptions import ToolError

import mcp_server


@pytest.fixture
def server(engine, genres, monkeypatch):
    # Use the small test dataset instead of loading the real one
    monkeypatch.setattr(mcp_server, "engine", engine)
    monkeypatch.setattr(mcp_server, "genres", genres)
    return mcp_server.mcp


def call_tool(server, name, arguments):
    async def run():
        return await server.call_tool(name, arguments)
    return anyio.run(run)


def test_server_has_all_tools(server):
    async def run():
        return await server.list_tools()

    names = {tool.name for tool in anyio.run(run)}
    assert names == {'search_tracks', 'recommend_by_features', 'recommend_similar', 'list_genres'}


def test_call_search_tracks(server):
    result = call_tool(server, 'search_tracks', {'query': 'party band'})

    assert not result.is_error
    tracks = result.structured_content['result']
    assert [track['track_id'] for track in tracks] == ['party1', 'party2']


def test_call_recommend_by_features(server):
    result = call_tool(server, 'recommend_by_features', {'energy': 0.9, 'genre': 'dance', 'limit': 5})

    tracks = result.structured_content['result']
    assert {track['genre'] for track in tracks} == {'dance'}


def test_call_list_genres(server):
    result = call_tool(server, 'list_genres', {})
    assert result.structured_content['result'] == ['acoustic', 'ambient', 'dance']


def test_unknown_genre_error_is_shown_to_the_ai(server):
    # The message must reach the AI, so it knows how to fix the call
    with pytest.raises(ToolError, match="Use list_genres"):
        call_tool(server, 'recommend_by_features', {'genre': 'polka'})


def test_unknown_track_error_is_shown_to_the_ai(server):
    with pytest.raises(ToolError, match="Use search_tracks"):
        call_tool(server, 'recommend_similar', {'track_id': 'missing'})


def test_missing_dataset_error_is_shown_to_the_ai(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_server, "engine", None)
    monkeypatch.setattr(mcp_server, "PROJECT_DIR", str(tmp_path))

    with pytest.raises(ToolError, match="Dataset not found"):
        call_tool(mcp_server.mcp, 'list_genres', {})
