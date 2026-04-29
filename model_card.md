# Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0** — Rule-Based Scoring + Gemini RAG

---

## 2. Intended Use

VibeFinder suggests the top-k songs from a 10-song catalog based on a user's preferred genre, mood, target energy level, and acoustic preference. It is a classroom demonstration system, not designed for real-world deployment. It is intended to show how transparent scoring algorithms and AI-generated explanations can work together in a recommender pipeline.

---

## 3. How the Model Works

The system works in two stages.

**Stage 1 — Retrieval:** Every song in the catalog is given a match score between 0 and 1. The score is the weighted sum of four factors: whether the song's genre matches the user's favorite (35% of the score), whether the mood matches (30%), how close the song's energy level is to the user's target (25%), and whether the acousticness aligns with the user's acoustic preference (10%). Songs are then ranked from highest to lowest score, and the top results are selected.

**Stage 2 — Generation (RAG):** The retrieved songs, along with all their attributes, are passed to Gemini. Gemini writes a short, conversational paragraph explaining why those specific songs were chosen. Because Gemini only sees the song data that was retrieved, it cannot invent songs that aren't in the catalog — this is the "retrieval-augmented" part of the design.

Confidence labels (High / Medium / Low) are shown next to each song based on its score.

---

## 4. Data

The catalog contains 10 manually curated songs stored in `data/songs.csv`. Each song has a genre (pop, lofi, rock, ambient, jazz, synthwave, or indie pop), a mood (happy, chill, intense, relaxed, moody, or focused), and numeric attributes for energy, tempo, valence, danceability, and acousticness.

The catalog is small and was not drawn from any real streaming platform. It reflects a limited, Western-leaning set of genres and does not include classical music, world music, hip-hop, R&B, country, or many other major categories. All numeric attributes were manually assigned.

---

## 5. Strengths

- The scoring is fully transparent — a user can see exactly why a song ranked where it did.
- Confidence labels make uncertainty visible rather than hiding it.
- The system works offline without any API key; the Gemini explanation is optional.
- Genre and mood matching are reliable when the catalog contains songs that match the user's preferences.
- The RAG design ensures Gemini cannot hallucinate songs or fabricate musical details.

---

## 6. Limitations and Bias

- **Binary genre matching:** "indie pop" and "pop" score as completely different genres despite being closely related. This means cross-genre users get lower scores even when the catalog has relevant songs.
- **Tiny catalog:** With only 10 songs, users asking for k=8 or more will receive low-confidence results that don't genuinely match their preferences.
- **No diversity enforcement:** The top results may all be from the same artist or subgenre if the catalog happens to cluster that way.
- **Static preferences:** The system treats every user session identically — there is no memory of prior listening behavior or feedback.
- **Acoustic preference is binary:** Users who enjoy both acoustic and non-acoustic songs are penalized because the model forces a yes/no choice.
- **Genre representation bias:** The catalog has 3 lofi songs, 2 pop songs, 1 rock, 1 ambient, 1 jazz, 1 synthwave, and 1 indie pop. Lofi users benefit from more catalog variety than, say, jazz users.

---

## 7. Evaluation

**Automated tests (7 tests, all passing):**
- Verified that recommendations are returned in descending score order.
- Verified that the k parameter correctly limits result count.
- Verified that load_songs returns the expected 10-song structure.
- Verified that the guardrail correctly rejects an energy value of 1.5.
- Verified that confidence labels appear in all explanations.

**Manual testing across 3 user profiles:**
1. Pop/happy/high-energy user → "Sunrise City" ranked #1 with score 0.98. Felt correct.
2. Lofi/chill/low-energy/acoustic user → "Library Rain" ranked #1 with score 0.93. Felt correct.
3. Jazz/focused user → Best jazz match scored only 0.55 because the catalog has only one jazz song and the energy didn't align closely. The system was honest about this with a "Medium" confidence label.

**Surprise:** The energy proximity component (25% weight) had a larger practical effect than expected. A perfect genre+mood match with mismatched energy scored lower than a mood-only match with close energy. Adjusting the weights to 40/35/15/10 improved jazz and ambient results but hurt lofi results, demonstrating the inherent trade-off in static weight schemes.

---

## 8. Future Work

- Add partial genre credit (e.g., treat "indie pop" as 0.6 match for "pop").
- Expand the catalog to 50+ songs with real audio feature data from a public music API.
- Add a feedback loop: let users rate recommendations so the system can adjust weights per session.
- Implement diversity scoring to avoid recommending five songs by the same artist.
- Add a collaborative filtering layer: recommend songs liked by users with similar profiles.

---

## 9. Personal Reflection

**What I learned:** Building the scoring algorithm made clear that recommendation systems are not neutral — every weight assignment is a design decision that advantages certain users. Choosing to weight genre at 35% over mood at 30% is an opinion about what matters more in a song match.

**What surprised me:** How much the small catalog size dominated the system's quality. Sophisticated scoring logic doesn't help when the catalog has only one jazz song and a user wants jazz recommendations.

**AI collaboration — helpful instance:** When designing the RAG prompt, Gemini suggested prefacing each song with its rank and score in the prompt context, which made the generated explanation reference specific songs more accurately. This was a genuine improvement I hadn't considered.

**AI collaboration — flawed instance:** Gemini initially suggested using cosine similarity on feature vectors rather than a weighted sum, which would have been harder to interpret and explain in the confidence labels. The simpler weighted sum approach is more transparent and better suited to this assignment's goal of explainability.

**How this changed my thinking:** Real music apps like Spotify or YouTube Music use collaborative filtering, embedding models, and listening history that make the "why" of a recommendation nearly impossible to explain. This project showed me that there is a real design tradeoff between accuracy and transparency — and that for applications where users should understand and trust the AI's decisions, simpler interpretable systems can be the better choice.
