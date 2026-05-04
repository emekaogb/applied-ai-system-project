import copy
from typing import Dict
from feedback import FeedbackEvent

ENERGY_LR = 0.05
ACOUSTIC_THRESHOLD = 0.6  # acousticness > this = "acoustic" song


def update_preferences(user_prefs: Dict, event: FeedbackEvent, reward: float) -> Dict:
    """Mutate user_prefs in-place based on feedback and return it."""
    _update_energy(user_prefs, event.song, reward)
    _update_categorical(user_prefs, event.song, reward, "genre", "favorite_genre")
    _update_categorical(user_prefs, event.song, reward, "mood", "favorite_mood")
    _update_acoustic(user_prefs, event.song, reward)
    _update_penalty(user_prefs, event.song, reward)
    return user_prefs


def _update_energy(user_prefs: Dict, song: Dict, reward: float) -> None:
    old = user_prefs["target_energy"]
    nudge = ENERGY_LR * reward * (float(song["energy"]) - old)
    user_prefs["target_energy"] = round(max(0.05, min(0.95, old + nudge)), 4)


def _update_categorical(user_prefs: Dict, song: Dict, reward: float,
                         field: str, pref_key: str) -> None:
    counts = user_prefs.setdefault("_vote_counts", {}).setdefault(field, {})
    value = song[field]  # always act on the skipped/played song's category

    if reward > 0:
        counts[value] = counts.get(value, 0) + round(reward * 2)
    else:
        counts[value] = counts.get(value, 0) + round(reward)  # reward is negative

    # Winning category becomes the new favorite
    if counts:
        user_prefs[pref_key] = max(counts, key=lambda k: counts[k])


def _update_penalty(user_prefs: Dict, song: Dict, reward: float) -> None:
    """
    Track a score multiplier (0.3–1.0) per genre and mood.
    Skips decay the multiplier by 15%; plays recover it by 10%.
    Applied in score_song so repeatedly skipped genres rank lower.
    """
    genre_penalties = user_prefs.setdefault("_genre_penalty", {})
    mood_penalties = user_prefs.setdefault("_mood_penalty", {})

    genre = song["genre"]
    mood = song["mood"]

    if reward < 0:
        genre_penalties[genre] = round(max(0.3, genre_penalties.get(genre, 1.0) * 0.85), 3)
        mood_penalties[mood] = round(max(0.3, mood_penalties.get(mood, 1.0) * 0.85), 3)
    else:
        genre_penalties[genre] = round(min(1.0, genre_penalties.get(genre, 1.0) * 1.10), 3)
        mood_penalties[mood] = round(min(1.0, mood_penalties.get(mood, 1.0) * 1.10), 3)


def _update_acoustic(user_prefs: Dict, song: Dict, reward: float) -> None:
    score = user_prefs.setdefault("_acoustic_score", -3 if not user_prefs.get("likes_acoustic") else 3)
    song_is_acoustic = float(song["acousticness"]) > ACOUSTIC_THRESHOLD

    if reward > 0:
        score += 1 if song_is_acoustic else -1
    else:
        score += -1 if song_is_acoustic else 1

    user_prefs["_acoustic_score"] = score
    user_prefs["likes_acoustic"] = score > 0


def preference_delta(old: Dict, new: Dict) -> list:
    """Return list of human-readable change strings between two preference snapshots."""
    lines = []

    if old.get("target_energy") != new.get("target_energy"):
        lines.append(f"[LEARNING] Energy target: {old['target_energy']:.2f} → {new['target_energy']:.2f}")

    if old.get("favorite_genre") != new.get("favorite_genre"):
        lines.append(f"[LEARNING] Favorite genre: {old['favorite_genre']} → {new['favorite_genre']}")

    if old.get("favorite_mood") != new.get("favorite_mood"):
        lines.append(f"[LEARNING] Favorite mood: {old['favorite_mood']} → {new['favorite_mood']}")

    if old.get("likes_acoustic") != new.get("likes_acoustic"):
        pref = "acoustic" if new["likes_acoustic"] else "electric/produced"
        lines.append(f"[LEARNING] Acoustic preference flipped → now prefers {pref}")

    genre_counts = new.get("_vote_counts", {}).get("genre", {})
    if genre_counts:
        top = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:4]
        lines.append("[LEARNING] Genre votes: " + "  ".join(f"{g}({v})" for g, v in top))

    penalized = [(g, p) for g, p in new.get("_genre_penalty", {}).items() if p < 1.0]
    if penalized:
        penalized.sort(key=lambda x: x[1])
        lines.append("[LEARNING] Genre penalties: " + "  ".join(f"{g}({p:.2f})" for g, p in penalized[:4]))

    return lines
