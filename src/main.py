"""
Command line runner for the Music Recommender Simulation.
Run with:  python -m src.main
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from guardrails import validate_user_prefs
from logger_config import setup_logging
from recommender import load_songs, recommend_songs


def main() -> None:
    setup_logging()

    songs = load_songs("data/songs.csv")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    is_valid, err = validate_user_prefs(user_prefs)
    if not is_valid:
        print(f"Invalid preferences: {err}")
        return

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for song, score, explanation in recommendations:
        print(f"  {song['title']} by {song['artist']} — Score: {score:.2f}")
        print(f"  {explanation}\n")


if __name__ == "__main__":
    main()
