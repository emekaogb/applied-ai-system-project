import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from feedback import FeedbackEvent

METRICS_DIR = Path(__file__).parent.parent / "data" / "metrics"


def record_event(user_name: str, event: FeedbackEvent, reward: float) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    path = METRICS_DIR / f"{user_name}.jsonl"
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "song_id": event.song["id"],
        "song_title": event.song["title"],
        "genre": event.song["genre"],
        "mood": event.song["mood"],
        "energy": float(event.song["energy"]),
        "score": event.score,
        "rank": event.rank,
        "played": event.played,
        "reward": reward,
        "pref_genre": event.user_prefs.get("favorite_genre", ""),
        "pref_mood": event.user_prefs.get("favorite_mood", ""),
        "pref_energy": event.user_prefs.get("target_energy", 0.0),
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _load_events(user_name: str) -> List[Dict]:
    path = METRICS_DIR / f"{user_name}.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def hit_rate(user_name: str, last_n: int) -> Optional[float]:
    """Return plays/total for the last N events, or None if not enough data."""
    events = _load_events(user_name)
    if len(events) < last_n:
        return None
    window = events[-last_n:]
    plays = sum(1 for e in window if e["played"])
    return plays / last_n


def print_session_summary(user_name: str, session_events: List[FeedbackEvent],
                           session_rewards: List[float],
                           energy_start: float, energy_end: float) -> None:
    total = len(session_events)
    plays = sum(1 for e in session_events if e.played)
    skips = total - plays
    avg_reward = sum(session_rewards) / total if total else 0.0

    print(f"\n{'='*55}")
    print(f"  Session Summary — {user_name}")
    print(f"{'='*55}")
    print(f"  Songs presented : {total}")
    print(f"  Played          : {plays}   Skipped : {skips}")
    print(f"  Hit rate        : {plays/total*100:.1f}%" if total else "  Hit rate        : n/a")
    print(f"  Avg reward      : {avg_reward:+.2f}")
    print(f"  Energy target   : {energy_start:.2f} → {energy_end:.2f}")

    rate_10 = hit_rate(user_name, 10)
    rate_100 = hit_rate(user_name, 100)
    if rate_10 is not None:
        print(f"  Hit rate (last 10)  : {rate_10*100:.1f}%")
    if rate_100 is not None:
        print(f"  Hit rate (last 100) : {rate_100*100:.1f}%")
    print(f"{'='*55}\n")
