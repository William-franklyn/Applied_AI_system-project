"""
Evaluation harness for VibeFinder.

Runs the recommender against predefined user profiles and prints a
structured results summary showing scores, confidence, and pass/fail
for each profile.

Run with:
    python eval.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from guardrails import validate_user_prefs
from logger_config import setup_logging
from recommender import load_songs, recommend_songs

setup_logging(log_dir="logs")

# ---------------------------------------------------------------------------
# Predefined evaluation profiles
# Each profile has an expected top genre to verify against the #1 result.
# ---------------------------------------------------------------------------
PROFILES = [
    {
        "name": "Pop Fan",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
        "expect_genre": "pop",
    },
    {
        "name": "Lofi Acoustic Listener",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
        "expect_genre": "lofi",
    },
    {
        "name": "Ambient Relaxer",
        "prefs": {"genre": "ambient", "mood": "relaxed", "energy": 0.30, "likes_acoustic": True},
        "expect_genre": "ambient",
    },
    {
        "name": "Rock Energizer",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
        "expect_genre": "rock",
    },
    {
        "name": "Jazz Explorer",
        "prefs": {"genre": "jazz", "mood": "focused", "energy": 0.50, "likes_acoustic": True},
        "expect_genre": "jazz",
    },
]

# Guardrail edge-case inputs — these should all be rejected before scoring
GUARDRAIL_CASES = [
    {"genre": "pop",   "mood": "happy", "energy": 1.5,  "likes_acoustic": False},  # energy out of range
    {"genre": "",      "mood": "chill", "energy": 0.5,  "likes_acoustic": False},  # missing genre
    {"genre": "metal", "mood": "happy", "energy": 0.8,  "likes_acoustic": False},  # invalid genre
    {"genre": "lofi",  "mood": "",      "energy": 0.4,  "likes_acoustic": True},   # missing mood
]

DIV  = "=" * 64
LINE = "-" * 64


def run_evaluation(songs: list) -> int:
    passed = 0

    print(f"\n{DIV}")
    print("  VibeFinder -- Recommendation Evaluation Report")
    print(DIV)

    for profile in PROFILES:
        name   = profile["name"]
        prefs  = profile["prefs"]
        expect = profile["expect_genre"]

        results = recommend_songs(prefs, songs, k=3)
        top_song, top_score, top_explanation = results[0]
        top_genre = top_song["genre"]

        ok     = top_genre == expect
        status = "PASS" if ok else "FAIL"
        conf   = "High" if top_score >= 0.7 else "Medium" if top_score >= 0.45 else "Low"
        if ok:
            passed += 1

        print(f"\n  Profile : {name}")
        print(f"  Prefs   : genre={prefs['genre']}, mood={prefs['mood']}, "
              f"energy={prefs['energy']}, acoustic={prefs['likes_acoustic']}")
        print(f"  #1 Song : \"{top_song['title']}\" by {top_song['artist']}")
        print(f"  Score   : {top_score:.2f}  |  Confidence: {conf}")
        print(f"  Why     : {top_explanation}")
        print(f"  Expect  : genre={expect}  |  Got: genre={top_genre}  |  [{status}]")
        print(LINE)

    return passed


def run_guardrail_checks() -> int:
    guard_passed = 0

    print(f"\n{DIV}")
    print("  VibeFinder -- Guardrail Validation Tests")
    print(DIV)

    for case in GUARDRAIL_CASES:
        is_valid, msg = validate_user_prefs(case)
        if not is_valid:
            guard_passed += 1
            result = "BLOCKED (correct)"
        else:
            result = "ALLOWED (unexpected -- guardrail missed this)"

        print(f"\n  Input  : {case}")
        print(f"  Result : {result}")
        if msg:
            print(f"  Reason : {msg}")
        print(LINE)

    return guard_passed


def main() -> None:
    songs = load_songs("data/songs.csv")

    rec_passed  = run_evaluation(songs)
    rec_total   = len(PROFILES)
    guard_passed = run_guardrail_checks()
    guard_total  = len(GUARDRAIL_CASES)

    print(f"\n{DIV}")
    print("  SUMMARY")
    print(DIV)
    print(f"  Recommendation checks : {rec_passed}/{rec_total} passed")
    print(f"  Guardrail checks      : {guard_passed}/{guard_total} correctly blocked")
    overall = rec_passed + guard_passed
    total   = rec_total + guard_total
    print(f"  Overall               : {overall}/{total} checks passed")
    print(DIV + "\n")


if __name__ == "__main__":
    main()
