# 🎧 Spotify Music Clustering & Recommendation Engine

An unsupervised machine learning system clustering 32,800+ tracks into acoustic archetypes using Principal Component Analysis (PCA), $k$-Means clustering, and high-dimensional Cosine Similarity vector search.

---

## 🛠️ Tech Stack & Methodology
* **Language & Storage:** Python, DuckDB SQL, Apache Parquet, NumPy, Pandas
* **Machine Learning:** Scikit-Learn (StandardScaler, PCA, KMeans, cosine_similarity)
* **Visualization:** Matplotlib, Seaborn

---

## 📊 Acoustic Archetype Centroid Profiles (k = 6)

The $k$-Means algorithm converged on 6 distinct acoustic clusters across 32,826 tracks, evaluated via Elbow SSE curvature and Silhouette Coefficient optimization:

| Cluster | Archetype Name | Volume | Dominant Acoustic Characteristics | Key Audio Metrics |
| :---: | :--- | :---: | :--- | :--- |
| **C0** | **Acoustic / Folk / Downtempo** | **4,635** | Highest acousticness, minimal electronic production, quietest loudness. | Acousticness: **0.522** \| Loudness: **-10.5 dB** |
| **C1** | **Upbeat Commercial Pop & Dance** | **10,677** | Peak catalog valence/happiness, elevated danceability, clean production. | Valence: **0.682** \| Danceability: **0.741** |
| **C2** | **Live Recordings & Concert Events** | **2,155** | Extreme liveness spike (audience/room resonance), high energy. | Liveness: **0.611** (vs. 0.16 catalog baseline) |
| **C3** | **Driving Rock, Metal & Fast EDM** | **8,569** | Highest catalog energy, loudest playback, fastest tempo, intense/moody mood. | Energy: **0.792** \| Tempo: **132.5 BPM** |
| **C4** | **Electronic & Atmospheric Instrumental** | **2,465** | Near-complete absence of vocals, synthesized and ambient textures. | Instrumentalness: **0.751** (vs. 0.08 baseline) |
| **C5** | **Rhythmic Urban, Hip-Hop & Rap** | **4,325** | Distinct speechiness peak (cadence/spoken vocals), high rhythmic groove. | Speechiness: **0.313** \| Danceability: **0.725** |

---

## 📈 Model Diagnostics & Visualizations

### 1. PCA Scree Plot & Variance Retention
The first 2 principal components capture **40.68%** of catalog variance. The full 80% threshold is surpassed at **6 components** (84.08%), reducing the feature space while eliminating high-dimensional noise.

![PCA Scree Plot](charts/pca_variance_scree.png)

### 2. Elbow Method & Silhouette Coefficient Optimization
Cluster evaluation across k in [2, 10] identified k=6 as the optimal balance between inertia reduction (SSE inflection) and cluster silhouette quality (S = 0.1573).

![Elbow & Silhouette Curves](charts/elbow_silhouette_curve.png)

### 3. 2D PCA Latent Space Projection
Global mapping of 32,800+ tracks projected onto PC1 (Acoustic vs. Energy axis) and PC2 (Danceability & Valence axis), demonstrating spatial separation across the 6 archetypes:

![PCA Latent Space](charts/latent_space_pca.png)

### 4. Acoustic Archetype Centroid Heatmap
Relative Z-score feature contrasts illustrating normalized deviations of each archetype from the catalog mean:

![Archetype Centroid Heatmap](charts/archetype_centroid_heatmap.png)

---

## 🎯 Content-Based Vector Recommendation Engine

The engine computes pairwise Cosine Similarity across the standardized 9-dimensional acoustic feature space:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

```bash
python scripts/recommend.py
