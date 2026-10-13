import duckdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pathlib import Path

DATA_DIR = Path("spotify_music_clustering/data")
CHARTS_DIR = Path("spotify_music_clustering/charts")
DB_PATH = DATA_DIR / "spotify_analytics.db"

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

def train_and_profile_clusters():
    print("Loading scaled features and track data...")
    X_scaled = np.load(DATA_DIR / "scaled_features.npy")
    
    # Load all track records directly in exact 1-to-1 row alignment
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df_full = con.execute(f"""
        SELECT 
            track_id,
            track_name,
            artists,
            release_year,
            popularity,
            {", ".join(FEATURE_COLUMNS)}
        FROM stg_spotify_tracks
        WHERE track_id IS NOT NULL
    """).df()
    con.close()
    
    df_full[FEATURE_COLUMNS] = df_full[FEATURE_COLUMNS].fillna(df_full[FEATURE_COLUMNS].median())
    
    print(f"Loaded {len(df_full):,} tracks matching feature matrix {X_scaled.shape}.")
    
    # 1. Fit KMeans (k = 6)
    print("Training KMeans model (k = 6, random_state = 42)...")
    kmeans = KMeans(n_clusters=6, random_state=42, n_init=15)
    cluster_labels = kmeans.fit_predict(X_scaled)
    df_full["cluster_id"] = cluster_labels
    
    # 2. Project high-dimensional vectors to 2D PCA coordinate plane
    print("Computing 2D PCA latent projections...")
    pca = PCA(n_components=2, random_state=42)
    pca_coords = pca.fit_transform(X_scaled)
    df_full["pca_1"] = pca_coords[:, 0]
    df_full["pca_2"] = pca_coords[:, 1]
    
    # 3. Calculate unscaled acoustic centroids per cluster
    centroid_summary = df_full.groupby("cluster_id")[FEATURE_COLUMNS].mean().round(3)
    counts = df_full["cluster_id"].value_counts().rename("track_count")
    centroid_summary = centroid_summary.join(counts)
    
    print("\n================ CLUSTER ACOUSTIC CENTROIDS ================")
    print(centroid_summary.to_string())
    print("============================================================\n")
    
    # 4. Map interpretable archetype names based on dominant centroid signatures
    archetype_labels = {}
    for cid, row in centroid_summary.iterrows():
        if row["instrumentalness"] >= 0.25:
            archetype_labels[cid] = f"Cluster {cid}: Ambient & Electronic Instrumental"
        elif row["acousticness"] >= 0.50:
            archetype_labels[cid] = f"Cluster {cid}: Acoustic / Folk / Downtempo"
        elif row["speechiness"] >= 0.15:
            archetype_labels[cid] = f"Cluster {cid}: Rhythmic Urban / Hip-Hop & Rap"
        elif row["energy"] >= 0.75 and row["valence"] >= 0.55:
            archetype_labels[cid] = f"Cluster {cid}: High-Energy Club Dance & EDM"
        elif row["energy"] >= 0.70 and row["valence"] < 0.45:
            archetype_labels[cid] = f"Cluster {cid}: Intense / Moody Rock & Dark Pop"
        else:
            archetype_labels[cid] = f"Cluster {cid}: Melodic Commercial Pop & R&B"
            
    df_full["archetype_name"] = df_full["cluster_id"].map(archetype_labels)
    
    # Export enriched dataset
    clustered_out = DATA_DIR / "clustered_tracks.parquet"
    df_full.to_parquet(clustered_out, index=False)
    print(f"Saved clustered dataset with archetypes -> {clustered_out}")
    
    # 5. Visualization 1: 2D PCA Latent Space Scatter
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=df_full.sample(n=10000, random_state=42),
        x="pca_1",
        y="pca_2",
        hue="archetype_name",
        palette="tab10",
        alpha=0.45,
        s=18,
        edgecolor=None
    )
    plt.title("Spotify Audio Latent Space: 2D PCA Projection (k = 6)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(f"PC 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance) - Acoustic vs. Energy Axis", fontsize=11)
    plt.ylabel(f"PC 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance) - Danceability & Valence Axis", fontsize=11)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, title="Acoustic Archetype")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    
    pca_chart = CHARTS_DIR / "latent_space_pca.png"
    plt.savefig(pca_chart, dpi=300)
    plt.close()
    print(f"Saved: {pca_chart}")
    
    # 6. Visualization 2: Acoustic Centroid Heatmap (Standardized comparison)
    centroid_norm = (centroid_summary[FEATURE_COLUMNS] - centroid_summary[FEATURE_COLUMNS].mean()) / centroid_summary[FEATURE_COLUMNS].std()
    centroid_norm.index = [archetype_labels[cid] for cid in centroid_norm.index]
    
    plt.figure(figsize=(11, 6))
    sns.heatmap(
        centroid_norm,
        cmap="coolwarm",
        annot=True,
        fmt=".2f",
        linewidths=0.8,
        cbar_kws={"label": "Relative Centroid Z-Score"}
    )
    plt.title("Acoustic Archetype Feature Contrasts (Normalized Centroids)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Audio Features", fontsize=11)
    plt.ylabel("Cluster Archetype", fontsize=11)
    plt.tight_layout()
    
    heatmap_chart = CHARTS_DIR / "archetype_centroid_heatmap.png"
    plt.savefig(heatmap_chart, dpi=300)
    plt.close()
    print(f"Saved: {heatmap_chart}")

if __name__ == "__main__":
    train_and_profile_clusters()
