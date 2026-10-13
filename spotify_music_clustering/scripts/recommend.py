import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

DATA_DIR = Path("spotify_music_clustering/data")

def load_recommender_assets():
    """Loads scaled feature vectors and clustered track metadata."""
    features_path = DATA_DIR / "scaled_features.npy"
    tracks_path = DATA_DIR / "clustered_tracks.parquet"
    
    if not features_path.exists() or not tracks_path.exists():
        raise FileNotFoundError("Required artifacts (scaled_features.npy, clustered_tracks.parquet) not found.")
        
    X_scaled = np.load(features_path)
    df_tracks = pd.read_parquet(tracks_path)
    return X_scaled, df_tracks

def recommend_similar_tracks(query_title: str, top_n: int = 5, restrict_to_cluster: bool = False) -> pd.DataFrame:
    """
    Computes pairwise Cosine Similarity across acoustic feature vectors
    to retrieve the top-N most acoustically identical tracks.
    """
    X_scaled, df_tracks = load_recommender_assets()
    
    # Locate candidate tracks by partial case-insensitive string match
    matches = df_tracks[df_tracks["track_name"].str.contains(query_title, case=False, na=False)]
    if matches.empty:
        print(f"No tracks found matching title: '{query_title}'")
        return pd.DataFrame()
        
    # Select the most popular match as the anchor track
    seed_idx = matches.sort_values(by="popularity", ascending=False).index[0]
    seed_track = df_tracks.iloc[seed_idx]
    seed_vector = X_scaled[seed_idx].reshape(1, -1)
    
    print(f"\n==================== SEED TRACK ====================")
    print(f"Title:       {seed_track['track_name']}")
    print(f"Artist(s):   {seed_track['artists']}")
    print(f"Year:        {seed_track['release_year']} | Popularity: {seed_track['popularity']}/100")
    print(f"Archetype:   {seed_track['archetype_name']}")
    print(f"====================================================")
    
    # Calculate cosine similarity across the feature matrix
    if restrict_to_cluster:
        cluster_mask = df_tracks["cluster_id"] == seed_track["cluster_id"]
        eval_indices = df_tracks[cluster_mask].index.to_numpy()
        similarities = cosine_similarity(seed_vector, X_scaled[eval_indices]).flatten()
        result_df = df_tracks.iloc[eval_indices].copy()
    else:
        similarities = cosine_similarity(seed_vector, X_scaled).flatten()
        result_df = df_tracks.copy()
        
    result_df["cosine_similarity"] = similarities
    
    # Filter out the query track itself and sort by similarity score descending
    recommendations = (
        result_df[result_df["track_id"] != seed_track["track_id"]]
        .sort_values(by="cosine_similarity", ascending=False)
        .drop_duplicates(subset=["track_name", "artists"])
        .head(top_n)
    )
    
    output_cols = [
        "track_name", 
        "artists", 
        "release_year", 
        "popularity", 
        "archetype_name", 
        "cosine_similarity"
    ]
    return recommendations[output_cols].reset_index(drop=True)

if __name__ == "__main__":
    X_scaled, df_tracks = load_recommender_assets()
    print(f"Loaded {len(df_tracks):,} tracks with {X_scaled.shape[1]}-dimensional audio embeddings.")
    
    # Test Query 1: Upbeat / Dance Pop Anchor
    test_query_1 = "Blinding Lights"
    print(f"\nSearching nearest acoustic neighbors for: '{test_query_1}'...")
    recs_1 = recommend_similar_tracks(test_query_1, top_n=5)
    if not recs_1.empty:
        print(recs_1.to_string(index=False))
        
    # Test Query 2: Acoustic / Downtempo Anchor
    test_query_2 = "Someone You Loved"
    print(f"\nSearching nearest acoustic neighbors for: '{test_query_2}'...")
    recs_2 = recommend_similar_tracks(test_query_2, top_n=5)
    if not recs_2.empty:
        print(recs_2.to_string(index=False))
