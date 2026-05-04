import sys
import os
import copy
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from recommender import score_song, recommend_songs
from evaluator import compute_reward
from feedback import FeedbackEvent
from learning import update_preferences

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SONGS = [
    {
        "id": 1, "title": "Pop Hit", "artist": "A",
        "genre": "pop", "mood": "happy",
        "energy": 0.82, "tempo_bpm": 118,
        "valence": 0.84, "danceability": 0.79, "acousticness": 0.18,
    },
    {
        "id": 2, "title": "Rock Song", "artist": "B",
        "genre": "rock", "mood": "intense",
        "energy": 0.91, "tempo_bpm": 152,
        "valence": 0.48, "danceability": 0.66, "acousticness": 0.10,
    },
    {
        "id": 3, "title": "Chill Lofi", "artist": "C",
        "genre": "lofi", "mood": "chill",
        "energy": 0.42, "tempo_bpm": 78,
        "valence": 0.56, "danceability": 0.62, "acousticness": 0.71,
    },
]

BASE_PREFS = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.8,
    "likes_acoustic": False,
    "_vote_counts": {"genre": {"pop": 5}, "mood": {"happy": 5}},
    "_acoustic_score": -3,
    "_genre_penalty": {},
    "_mood_penalty": {},
}


def prefs(**overrides):
    p = copy.deepcopy(BASE_PREFS)
    p.update(overrides)
    return p


def make_event(song, played, rank=1, score=0.5):
    return FeedbackEvent(
        song=song,
        user_prefs=copy.deepcopy(BASE_PREFS),
        score=score,
        played=played,
        rank=rank,
    )


# ---------------------------------------------------------------------------
# score_song — scoring correctness
# ---------------------------------------------------------------------------

def test_genre_match_boosts_score():
    """A song matching the favorite genre should outscore a non-matching one."""
    pop_score, _ = score_song(BASE_PREFS, SONGS[0])   # pop matches
    rock_score, _ = score_song(BASE_PREFS, SONGS[1])  # rock does not
    assert pop_score > rock_score


def test_score_bounded_zero_to_one():
    """All song scores must stay in [0, 1]."""
    for song in SONGS:
        score, _ = score_song(BASE_PREFS, song)
        assert 0.0 <= score <= 1.0, f"Score {score:.3f} out of bounds for '{song['title']}'"


def test_perfect_match_scores_near_one():
    """A song matching genre, mood, and energy should score close to 1.0."""
    score, _ = score_song(BASE_PREFS, SONGS[0])  # pop/happy/0.82 vs target pop/happy/0.80
    assert score >= 0.90


def test_genre_penalty_lowers_score():
    """A penalized genre should score lower than the same song without a penalty."""
    p_no_penalty = prefs()
    p_penalized = prefs(**{"_genre_penalty": {"rock": 0.5}})

    score_normal, _ = score_song(p_no_penalty, SONGS[1])
    score_penalized, _ = score_song(p_penalized, SONGS[1])
    assert score_penalized < score_normal


def test_genre_penalty_does_not_affect_other_genres():
    """A rock penalty must not change the score of a pop song."""
    p_no_penalty = prefs()
    p_penalized = prefs(**{"_genre_penalty": {"rock": 0.5}})

    score_before, _ = score_song(p_no_penalty, SONGS[0])
    score_after, _ = score_song(p_penalized, SONGS[0])
    assert score_before == score_after


# ---------------------------------------------------------------------------
# recommend_songs — ranking correctness
# ---------------------------------------------------------------------------

def test_recommend_returns_k_songs():
    recs = recommend_songs(BASE_PREFS, SONGS, k=2)
    assert len(recs) == 2


def test_recommend_sorted_by_score_descending():
    recs = recommend_songs(BASE_PREFS, SONGS, k=3)
    scores = [r[1] for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_recommend_top_song_matches_genre():
    """With a pop profile, the top recommendation should be a pop song."""
    recs = recommend_songs(BASE_PREFS, SONGS, k=3)
    assert recs[0][0]["genre"] == "pop"


# ---------------------------------------------------------------------------
# compute_reward — reward signal correctness
# ---------------------------------------------------------------------------

def test_play_gives_positive_reward():
    event = make_event(SONGS[0], played=True, rank=1)
    reward, _ = compute_reward(event)
    assert reward > 0


def test_skip_gives_negative_reward():
    event = make_event(SONGS[1], played=False, rank=2)
    reward, _ = compute_reward(event)
    assert reward < 0


def test_rank1_play_rewards_more_than_rank5():
    """Playing the top pick should give a higher reward than playing the 5th pick."""
    e1 = make_event(SONGS[0], played=True, rank=1)
    e5 = make_event(SONGS[0], played=True, rank=5)
    r1, _ = compute_reward(e1)
    r5, _ = compute_reward(e5)
    assert r1 > r5


def test_high_confidence_skip_penalizes_more():
    """Skipping a high-score recommendation should cost more than skipping a borderline one."""
    e_high = make_event(SONGS[0], played=False, rank=1, score=0.95)
    e_low = make_event(SONGS[0], played=False, rank=1, score=0.20)
    r_high, _ = compute_reward(e_high)
    r_low, _ = compute_reward(e_low)
    assert r_high < r_low  # more negative = stronger penalty


# ---------------------------------------------------------------------------
# learning — profile update correctness
# ---------------------------------------------------------------------------

def test_energy_nudges_toward_played_song():
    p = prefs(target_energy=0.5)
    song = {**SONGS[0], "energy": 0.9}
    event = FeedbackEvent(song=song, user_prefs=copy.deepcopy(p), score=0.8, played=True, rank=1)
    reward, _ = compute_reward(event)
    old = p["target_energy"]
    update_preferences(p, event, reward)
    assert p["target_energy"] > old


def test_energy_nudges_away_from_skipped_song():
    p = prefs(target_energy=0.5)
    song = {**SONGS[1], "energy": 0.9}
    event = FeedbackEvent(song=song, user_prefs=copy.deepcopy(p), score=0.3, played=False, rank=3)
    reward, _ = compute_reward(event)
    old = p["target_energy"]
    update_preferences(p, event, reward)
    assert p["target_energy"] < old


def test_skip_penalizes_skipped_genre_not_current_favorite():
    """Skipping a rock song must penalize rock, not pop (the current favorite)."""
    p = prefs()
    event = FeedbackEvent(song=SONGS[1], user_prefs=copy.deepcopy(p),
                          score=0.3, played=False, rank=2)
    reward, _ = compute_reward(event)
    update_preferences(p, event, reward)
    assert p["_genre_penalty"].get("rock", 1.0) < 1.0
    assert p["_genre_penalty"].get("pop", 1.0) == 1.0


def test_play_recovers_genre_penalty():
    """Playing a penalized genre should bring its multiplier back toward 1.0."""
    p = prefs(**{"_genre_penalty": {"pop": 0.7}})
    event = FeedbackEvent(song=SONGS[0], user_prefs=copy.deepcopy(p),
                          score=0.95, played=True, rank=1)
    reward, _ = compute_reward(event)
    update_preferences(p, event, reward)
    assert p["_genre_penalty"]["pop"] > 0.7


def test_energy_stays_within_bounds():
    """Energy target must never go below 0.05 or above 0.95."""
    p = prefs(target_energy=0.05)
    song = {**SONGS[1], "energy": 0.0}
    event = FeedbackEvent(song=song, user_prefs=copy.deepcopy(p),
                          score=0.2, played=False, rank=1)
    reward, _ = compute_reward(event)
    update_preferences(p, event, reward)
    assert p["target_energy"] >= 0.05
