from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FeedbackEvent:
    song: Dict
    user_prefs: Dict
    score: float
    played: bool
    rank: int


def get_feedback(song: Dict, rank: int, score: float, reasons: List[str]) -> FeedbackEvent:
    print(f"\n{'─'*50}")
    print(f"  #{rank}  {song['title']} by {song['artist']}")
    print(f"       Score: {score:.2f}  |  Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {float(song['energy']):.2f}")
    print(f"  Why recommended:")
    for r in reasons:
        print(f"    {r}")

    while True:
        answer = input("\n  Play this song? (Y/N): ").strip().lower()
        if answer in ("y", "n"):
            return FeedbackEvent(
                song=song,
                user_prefs={},  # caller fills this in before passing to evaluator/learning
                score=score,
                played=(answer == "y"),
                rank=rank,
            )
        print("  Please enter Y or N.")
