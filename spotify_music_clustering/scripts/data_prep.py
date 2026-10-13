import duckdb
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path

DB_PATH = Path("spotify_music_clustering/data/spotify_analytics.db")
DATA_DIR = Path("spotify_music_clustering/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLUMNS = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]

def load_and_scale_features():
    print(f"Connecting to {DB_PATH}...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    
    query = f"""
    SELECT 
        track_id,
        track_name,
        artists,
        release_year,
        popularity,
        {", ".join(FEATURE_COLUMNS)}
    FROM stg_spotify_tracks
    WHERE track_id IS NOT NULL
    """
    df = con.execute(query).df()
    con.close()
    
    df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(df[FEATURE_COLUMNS].median())
    
    print(f"Loaded {len(df):,} tracks. Fitting StandardScaler...")
    scaler = StandardScaler()
    scaled_array = scaler.fit_transform(df[FEATURE_COLUMNS])
    
    # Export artifacts
    df_metadata = df[["track_id", "track_name", "artists", "release_year", "popularity"]]
    metadata_out = DATA_DIR / "track_metadata.parquet"
    df_metadata.to_parquet(metadata_out, index=False)
    
    features_out = DATA_DIR / "scaled_features.npy"
    np.save(features_out, scaled_array)
    
    print(f"Processed feature matrix: {scaled_array.shape}")
    print(f"Saved metadata: {metadata_out}")
    print(f"Saved feature array: {features_out}")
    return df_metadata, scaled_array

if __name__ == "__main__":
    load_and_scale_features()
