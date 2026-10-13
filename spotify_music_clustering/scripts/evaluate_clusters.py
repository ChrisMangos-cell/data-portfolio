import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pathlib import Path

DATA_DIR = Path("spotify_music_clustering/data")
CHARTS_DIR = Path("spotify_music_clustering/charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

def evaluate_pca_variance(X: np.ndarray):
    """
    Fits PCA on standardized audio features and generates a Scree plot
    tracking individual and cumulative explained variance.
    """
    pca_full = PCA().fit(X)
    cum_var = np.cumsum(pca_full.explained_variance_ratio_)
    
    print("\n--- PCA Explained Variance Breakdown ---")
    for idx, (var, cum) in enumerate(zip(pca_full.explained_variance_ratio_, cum_var), start=1):
        print(f"PC{idx:02d}: {var*100:5.2f}% | Cumulative: {cum*100:5.2f}%")
        
    n_80 = int(np.argmax(cum_var >= 0.80) + 1)
    n_90 = int(np.argmax(cum_var >= 0.90) + 1)
    print(f"\nComponents required for >= 80% variance: {n_80}")
    print(f"Components required for >= 90% variance: {n_90}")

    # Generate Scree & Cumulative Variance Chart
    fig, ax1 = plt.subplots(figsize=(10, 5))
    components = np.arange(1, len(cum_var) + 1)
    
    ax1.bar(components, pca_full.explained_variance_ratio_ * 100, color="#1f77b4", alpha=0.7, label="Individual Variance (%)")
    ax1.set_xlabel("Principal Component", fontsize=11)
    ax1.set_ylabel("Individual Explained Variance (%)", color="#1f77b4", fontsize=11)
    ax1.set_xticks(components)
    
    ax2 = ax1.twinx()
    ax2.plot(components, cum_var * 100, color="#e6550d", marker="o", linewidth=2, label="Cumulative Variance (%)")
    ax2.axhline(80, color="gray", linestyle="--", alpha=0.7, label="80% Threshold")
    ax2.set_ylabel("Cumulative Explained Variance (%)", color="#e6550d", fontsize=11)
    
    plt.title("PCA Scree Plot: Audio Feature Variance Retention", fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    scree_path = CHARTS_DIR / "pca_variance_scree.png"
    plt.savefig(scree_path, dpi=300)
    plt.close()
    print(f"Saved: {scree_path}")
    return pca_full

def evaluate_optimal_k(X: np.ndarray, k_range=range(2, 11)):
    """
    Computes KMeans inertia (Elbow method) and Silhouette scores.
    Uses a 10,000-sample subset for Silhouette calculation to prevent O(N^2) memory overhead.
    """
    inertias = []
    silhouette_scores = []
    
    print("\n--- Evaluating KMeans Clustering Metrics (k = 2 to 10) ---")
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        inertias.append(kmeans.inertia_)
        sil = silhouette_score(X, labels, sample_size=10000, random_state=42)
        silhouette_scores.append(sil)
        print(f"k = {k:02d} | Inertia: {kmeans.inertia_:10,.1f} | Silhouette Score: {sil:.4f}")

    # Plot Elbow & Silhouette Dual Curve
    fig, ax1 = plt.subplots(figsize=(10, 5))
    k_vals = list(k_range)
    
    ax1.plot(k_vals, inertias, color="#2ca02c", marker="s", linewidth=2, label="Inertia (SSE)")
    ax1.set_xlabel("Number of Clusters (k)", fontsize=11)
    ax1.set_ylabel("Inertia (Sum of Squared Errors)", color="#2ca02c", fontsize=11)
    ax1.set_xticks(k_vals)
    ax1.grid(True, linestyle="--", alpha=0.4)
    
    ax2 = ax1.twinx()
    ax2.plot(k_vals, silhouette_scores, color="#9467bd", marker="^", linewidth=2, label="Silhouette Score")
    ax2.set_ylabel("Silhouette Coefficient", color="#9467bd", fontsize=11)
    
    plt.title("Elbow Method & Silhouette Optimization Curve", fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    curve_path = CHARTS_DIR / "elbow_silhouette_curve.png"
    plt.savefig(curve_path, dpi=300)
    plt.close()
    print(f"Saved: {curve_path}")

if __name__ == "__main__":
    X_scaled = np.load(DATA_DIR / "scaled_features.npy")
    print(f"Loaded feature matrix: {X_scaled.shape}")
    evaluate_pca_variance(X_scaled)
    evaluate_optimal_k(X_scaled)
