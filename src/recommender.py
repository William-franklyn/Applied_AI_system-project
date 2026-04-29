import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_song(song: Dict, user_prefs: Dict) -> float:
    genre_score = 1.0 if song["genre"].lower() == user_prefs.get("genre", "").lower() else 0.0
    mood_score = 1.0 if song["mood"].lower() == user_prefs.get("mood", "").lower() else 0.0
    energy_score = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    acoustic_raw = song["acousticness"]
    acoustic_score = acoustic_raw if user_prefs.get("likes_acoustic", False) else (1.0 - acoustic_raw)

    return (0.35 * genre_score +
            0.30 * mood_score +
            0.25 * energy_score +
            0.10 * acoustic_score)


def _build_rule_explanation(song: Dict, user_prefs: Dict, score: float) -> str:
    parts = []
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        parts.append(f"matches your favorite genre ({song['genre']})")
    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        parts.append(f"fits your '{song['mood']}' mood")
    energy_diff = abs(song["energy"] - user_prefs.get("energy", 0.5))
    if energy_diff < 0.1:
        parts.append("has very close energy to your target")
    elif energy_diff < 0.2:
        parts.append("has similar energy to your target")
    if not parts:
        parts.append("is a reasonable match for your overall taste")
    confidence = "High" if score >= 0.7 else "Medium" if score >= 0.45 else "Low"
    return f"[Confidence: {confidence}] " + "; ".join(parts).capitalize() + "."


class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        songs_as_dicts = [s.__dict__ for s in self.songs]
        results = recommend_songs(user_dict, songs_as_dicts, k)
        id_to_song = {s.id: s for s in self.songs}
        return [id_to_song[r[0]["id"]] for r in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        score = _score_song(song.__dict__, user_dict)
        return _build_rule_explanation(song.__dict__, user_dict, score)


def load_songs(csv_path: str) -> List[Dict]:
    df = pd.read_csv(csv_path)
    songs = df.to_dict(orient="records")
    logger.info(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    if not songs:
        logger.warning("recommend_songs called with empty song list")
        return []

    k = max(1, min(k, len(songs)))

    scored = []
    for song in songs:
        score = _score_song(song, user_prefs)
        explanation = _build_rule_explanation(song, user_prefs, score)
        scored.append((song, round(score, 4), explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    logger.info(f"Top result: '{scored[0][0]['title']}' score={scored[0][1]}")
    return scored[:k]
