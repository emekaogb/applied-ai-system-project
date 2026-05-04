import copy
import json
from pathlib import Path
from typing import Dict, List

from recommender import recommend_songs, load_songs
from feedback import get_feedback, FeedbackEvent
from evaluator import compute_reward, compute_session_stats
from learning import update_preferences, preference_delta
from metrics import record_event, print_session_summary

PROFILES_DIR = Path(__file__).parent.parent / "data" / "profiles"


def load_user_profile(user_name: str, default_prefs: Dict) -> Dict:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = PROFILES_DIR / f"{user_name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    save_user_profile(user_name, default_prefs)
    return copy.deepcopy(default_prefs)


def save_user_profile(user_name: str, user_prefs: Dict) -> None:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = PROFILES_DIR / f"{user_name}.json"
    with open(path, "w") as f:
        json.dump(user_prefs, f, indent=2)


def run_interactive_session(user_name: str, user_prefs: Dict,
                             songs: List[Dict], k: int = 5) -> None:
    print(f"\nStarting session for {user_name}")
    print(f"Preferences: {user_prefs['favorite_genre']} / {user_prefs['favorite_mood']} "
          f"| energy target: {user_prefs['target_energy']:.2f} "
          f"| acoustic: {user_prefs['likes_acoustic']}")

    session_events: List[FeedbackEvent] = []
    session_rewards: List[float] = []
    energy_start = user_prefs["target_energy"]

    while True:
        recs = recommend_songs(user_prefs, songs, k=k)

        print(f"\n{'='*55}")
        print(f"  Recommendations for {user_name}")
        print(f"{'='*55}")

        for rank, (song, score, reasons) in enumerate(recs, start=1):
            event = get_feedback(song, rank, score, reasons)

            # Stamp prefs snapshot onto event before learning mutates them
            event.user_prefs = copy.deepcopy(user_prefs)

            reward, explanation = compute_reward(event)
            print(f"\n  [REWARD] {explanation}")

            old_prefs = copy.deepcopy(user_prefs)
            update_preferences(user_prefs, event, reward)
            save_user_profile(user_name, user_prefs)
            record_event(user_name, event, reward)

            for line in preference_delta(old_prefs, user_prefs):
                print(f"  {line}")

            session_events.append(event)
            session_rewards.append(reward)

        answer = input("\nGet another batch of recommendations? (Y/N): ").strip().lower()
        if answer != "y":
            break

    print_session_summary(
        user_name, session_events, session_rewards,
        energy_start, user_prefs["target_energy"]
    )


def run_demo_session(songs: List[Dict]) -> None:
    """Non-interactive demo — original 3-user output."""
    users = [
        {"name": "Alex (Pop Energy Lover)",
         "prefs": {"favorite_genre": "pop", "favorite_mood": "happy",
                   "target_energy": 0.8, "likes_acoustic": False}},
        {"name": "Jordan (Chill Lofi Listener)",
         "prefs": {"favorite_genre": "lofi", "favorite_mood": "chill",
                   "target_energy": 0.4, "likes_acoustic": True}},
        {"name": "Casey (Rock Intensity Seeker)",
         "prefs": {"favorite_genre": "rock", "favorite_mood": "intense",
                   "target_energy": 0.9, "likes_acoustic": False}},
    ]
    for user in users:
        recs = recommend_songs(user["prefs"], songs, k=5)
        print(f"\n{'='*60}")
        print(f"Recommendations for {user['name']}")
        print("="*60)
        for i, (song, score, reasons) in enumerate(recs, 1):
            print(f"{i}. {song['title']} by {song['artist']}")
            print(f"   Score: {score:.2f} | Genre: {song['genre']} | Mood: {song['mood']}")
            print(f"   Why recommended:")
            for r in reasons:
                print(f"      {r}")
            print()
