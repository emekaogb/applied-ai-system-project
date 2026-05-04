from typing import Dict, List, Tuple
from feedback import FeedbackEvent


def compute_reward(event: FeedbackEvent) -> Tuple[float, str]:
    """
    Returns (reward, explanation).

    Play:  base +1.0, scaled down slightly by rank (rank 1 = full credit).
    Skip:  base -0.5, scaled up by model confidence (high score + skip = stronger penalty).

    rank_multiplier: 1.0 at rank 1, -0.05 per additional rank position.
    """
    if event.played:
        rank_multiplier = max(0.75, 1.0 - (event.rank - 1) * 0.05)
        reward = round(1.0 * rank_multiplier, 3)
        explanation = f"Rank {event.rank} play → reward = +{reward:.2f}"
    else:
        # Higher model confidence on a skip = stronger negative signal
        confidence_scale = 0.5 + 0.5 * event.score
        reward = round(-0.5 * confidence_scale, 3)
        explanation = f"Rank {event.rank} skip (score={event.score:.2f}) → reward = {reward:.2f}"

    return reward, explanation


def compute_session_stats(events: List[FeedbackEvent], rewards: List[float]) -> Dict:
    total = len(events)
    plays = sum(1 for e in events if e.played)
    skips = total - plays
    hit_rate = plays / total if total > 0 else 0.0
    avg_reward = sum(rewards) / total if total > 0 else 0.0
    return {
        "total": total,
        "plays": plays,
        "skips": skips,
        "hit_rate": hit_rate,
        "avg_reward": avg_reward,
    }
