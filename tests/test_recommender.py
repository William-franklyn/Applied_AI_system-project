import os

from guardrails import validate_user_prefs
from recommender import Recommender, Song, UserProfile, load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_load_songs_returns_list_of_dicts():
    songs = load_songs(DATA_PATH)
    assert isinstance(songs, list)
    assert len(songs) == 10
    required_keys = {"id", "title", "artist", "genre", "mood", "energy", "acousticness"}
    assert required_keys.issubset(set(songs[0].keys()))


def test_recommend_songs_respects_k():
    songs = load_songs(DATA_PATH)
    user = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    results = recommend_songs(user, songs, k=3)
    assert len(results) == 3
    assert all(len(r) == 3 for r in results)


def test_recommend_songs_sorted_descending():
    songs = load_songs(DATA_PATH)
    user = {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}
    results = recommend_songs(user, songs, k=5)
    scores = [r[1] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_guardrail_rejects_invalid_energy():
    bad_prefs = {"genre": "pop", "mood": "happy", "energy": 1.5}
    is_valid, msg = validate_user_prefs(bad_prefs)
    assert not is_valid
    assert "energy" in msg.lower()


def test_explain_recommendation_contains_confidence():
    user = UserProfile("pop", "happy", 0.8, False)
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert "[Confidence:" in explanation
