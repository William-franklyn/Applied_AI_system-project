from typing import Tuple

VALID_GENRES = {"pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop"}
VALID_MOODS = {"happy", "chill", "intense", "relaxed", "moody", "focused"}


def validate_user_prefs(user_prefs: dict) -> Tuple[bool, str]:
    """Returns (is_valid, error_message). error_message is empty when valid."""
    genre = user_prefs.get("genre", "").strip().lower()
    mood = user_prefs.get("mood", "").strip().lower()
    energy = user_prefs.get("energy", -1)

    if not genre:
        return False, "Genre is required."
    if genre not in VALID_GENRES:
        return False, f"Unknown genre '{genre}'. Valid options: {sorted(VALID_GENRES)}"
    if not mood:
        return False, "Mood is required."
    if mood not in VALID_MOODS:
        return False, f"Unknown mood '{mood}'. Valid options: {sorted(VALID_MOODS)}"
    if not isinstance(energy, (int, float)) or not (0.0 <= float(energy) <= 1.0):
        return False, f"Energy must be a number between 0.0 and 1.0, got: {energy!r}"

    return True, ""
