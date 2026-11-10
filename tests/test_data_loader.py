import pytest

from src.data_loader import DataLoader, find_dataset


def test_normalized_features_are_between_0_and_1(loader):
    for col in loader.feature_columns:
        values = loader.data[f"{col}_norm"]
        assert values.min() >= 0.0
        assert values.max() <= 1.0


def test_rows_with_missing_features_are_removed(loader):
    assert 'broken1' not in loader.data['track_id'].values


def test_duplicates_keep_most_popular_version(loader):
    dance_all_night = loader.data[loader.data['track_name'] == 'Dance All Night']
    assert len(dance_all_night) == 1
    assert dance_all_night.iloc[0]['track_id'] == 'party1'


def test_missing_artist_name_becomes_unknown(loader):
    mystery = loader.data[loader.data['track_id'] == 'mystery1'].iloc[0]
    assert mystery['artist_name'] == 'Unknown'


def test_feature_ranges_use_real_units(loader):
    assert loader.feature_ranges['tempo'] == (70.0, 128.0)
    assert loader.feature_ranges['loudness'] == (-25.0, -4.0)


def test_missing_column_raises_error(raw_data):
    with pytest.raises(ValueError):
        DataLoader("unused.parquet").prepare_data(raw_data.drop(columns=['tempo']))


def test_get_genres(loader):
    assert loader.get_genres() == ['acoustic', 'ambient', 'dance']


def test_load_csv_file(tmp_path, raw_data):
    file_path = tmp_path / "spotify_data.csv"
    raw_data.to_csv(file_path)

    data = DataLoader(str(file_path)).prepare_data()
    assert len(data) == 6


def test_load_parquet_file(tmp_path, raw_data):
    file_path = tmp_path / "dataset.parquet"
    raw_data.to_parquet(file_path)

    data = DataLoader(str(file_path)).prepare_data()
    assert len(data) == 6


def test_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        DataLoader(str(tmp_path / "missing.csv")).prepare_data()


def test_find_dataset_prefers_parquet(tmp_path, raw_data):
    assert find_dataset(str(tmp_path)) is None

    raw_data.to_csv(tmp_path / "spotify_data.csv")
    assert find_dataset(str(tmp_path)).endswith("spotify_data.csv")

    raw_data.to_parquet(tmp_path / "dataset.parquet")
    assert find_dataset(str(tmp_path)).endswith("dataset.parquet")
