
CREATE OR REPLACE TABLE stg_spotify_tracks AS
SELECT 
    track_id,
    track_name,
    artists,
    TRY_CAST(release_year AS INTEGER) AS release_year,
    TRY_CAST(popularity AS INTEGER) AS popularity,
    TRY_CAST(duration_ms AS INTEGER) AS duration_ms,
    TRY_CAST(is_explicit AS INTEGER) AS is_explicit,
    -- Continuous audio feature vector
    TRY_CAST(danceability AS DOUBLE) AS danceability,
    TRY_CAST(energy AS DOUBLE) AS energy,
    TRY_CAST(key AS INTEGER) AS musical_key,
    TRY_CAST(loudness AS DOUBLE) AS loudness,
    TRY_CAST(mode AS INTEGER) AS mode_modality,
    TRY_CAST(speechiness AS DOUBLE) AS speechiness,
    TRY_CAST(acousticness AS DOUBLE) AS acousticness,
    TRY_CAST(instrumentalness AS DOUBLE) AS instrumentalness,
    TRY_CAST(liveness AS DOUBLE) AS liveness,
    TRY_CAST(valence AS DOUBLE) AS valence,
    TRY_CAST(tempo AS DOUBLE) AS tempo
FROM raw_tracks
WHERE track_id IS NOT NULL
  AND track_name IS NOT NULL
  AND duration_ms BETWEEN 30000 AND 1800000;
