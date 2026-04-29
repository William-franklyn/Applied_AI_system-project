import logging
import os
from typing import Dict, List, Tuple

from google import genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_ai_explanation(
    user_prefs: Dict,
    top_songs: List[Tuple[Dict, float, str]],
    model: str = "gemini-2.0-flash-lite",
) -> str:
    """
    RAG generation layer: takes retrieved top-k songs and user preferences,
    returns a Gemini-generated natural language explanation.
    Falls back gracefully if the API key is missing or the call fails.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set; skipping AI explanation")
        return "[AI explanation unavailable: set GEMINI_API_KEY in your .env file to enable this feature]"

    song_lines = []
    for i, (song, score, _) in enumerate(top_songs, 1):
        song_lines.append(
            f"{i}. \"{song['title']}\" by {song['artist']} "
            f"(genre: {song['genre']}, mood: {song['mood']}, "
            f"energy: {song['energy']:.2f}, "
            f"acousticness: {song['acousticness']:.2f}, "
            f"match score: {score:.2f})"
        )
    songs_context = "\n".join(song_lines)

    user_context = (
        f"Favorite genre: {user_prefs.get('genre', 'any')}, "
        f"Favorite mood: {user_prefs.get('mood', 'any')}, "
        f"Target energy level: {user_prefs.get('energy', 0.5):.1f}/1.0, "
        f"Likes acoustic: {user_prefs.get('likes_acoustic', False)}"
    )

    prompt = (
        "You are a friendly music recommendation assistant.\n\n"
        f"A listener has these preferences:\n{user_context}\n\n"
        f"Based on their preferences, the system retrieved and ranked these songs:\n{songs_context}\n\n"
        "Write a short, conversational paragraph (3-4 sentences) explaining why these songs were chosen "
        "for this listener. Be specific about the musical qualities that match their preferences. "
        "Do not invent any song details — only reference what is listed above. Keep it warm and encouraging."
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
        explanation = response.text.strip()
        logger.info(f"Gemini explanation generated ({len(explanation)} chars)")
        return explanation
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"[AI explanation unavailable: {str(e)}]"
