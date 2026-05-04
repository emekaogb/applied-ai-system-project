"""
Music Recommender — CLI entry point.

Usage:
  python -m src.main                        # interactive mode (default user: alex)
  python -m src.main --user jordan          # interactive mode for jordan
  python -m src.main --demo                 # non-interactive demo (original 3-user output)
  python -m src.main --user casey --k 3    # 3 songs per batch
"""

import argparse
import sys
from pathlib import Path

# Allow running as `python -m src.main` or `python src/main.py`
sys.path.insert(0, str(Path(__file__).parent))

from recommender import load_songs
from session import load_user_profile, run_interactive_session, run_demo_session

SONGS_CSV = Path(__file__).parent.parent / "data" / "songs.csv"

BUILTIN_USERS = {
    "alex": {
        "name": "Alex",
        "prefs": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
            "_vote_counts": {"genre": {"pop": 5}, "mood": {"happy": 5}},
            "_acoustic_score": -3,
            "_genre_penalty": {},
            "_mood_penalty": {},
        },
    },
    "jordan": {
        "name": "Jordan",
        "prefs": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.4,
            "likes_acoustic": True,
            "_vote_counts": {"genre": {"lofi": 5}, "mood": {"chill": 5}},
            "_acoustic_score": 3,
            "_genre_penalty": {},
            "_mood_penalty": {},
        },
    },
    "casey": {
        "name": "Casey",
        "prefs": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.9,
            "likes_acoustic": False,
            "_vote_counts": {"genre": {"rock": 5}, "mood": {"intense": 5}},
            "_acoustic_score": -3,
            "_genre_penalty": {},
            "_mood_penalty": {},
        },
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender with RL feedback loop")
    parser.add_argument(
        "--demo", action="store_true",
        help="Run non-interactive demo for all 3 built-in users"
    )
    parser.add_argument(
        "--user", choices=list(BUILTIN_USERS.keys()), default="alex",
        help="Which user profile to load for interactive mode (default: alex)"
    )
    parser.add_argument(
        "--k", type=int, default=5,
        help="Number of songs to recommend per batch (default: 5)"
    )
    args = parser.parse_args()

    songs = load_songs(str(SONGS_CSV))

    if args.demo:
        run_demo_session(songs)
    else:
        selected = BUILTIN_USERS[args.user]
        user_prefs = load_user_profile(selected["name"], selected["prefs"])
        run_interactive_session(selected["name"], user_prefs, songs, k=args.k)


if __name__ == "__main__":
    main()
