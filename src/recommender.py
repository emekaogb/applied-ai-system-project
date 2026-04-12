from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    
    songs = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numerical fields to float for mathematical operations
            row['id'] = int(row['id'])
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            songs.append(row)
    
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences (40% genre, 30% mood, 20% energy, 10% other) with reasoning."""
    reasons = []
    score_components = {}
    
    # Genre match (40%)
    genre_weight = 0.40
    genre_match = 1.0 if song['genre'].lower() == user_prefs['favorite_genre'].lower() else 0.0
    score_components['genre'] = genre_match * genre_weight
    if genre_match == 1.0:
        reasons.append(f"✓ Genre match: {song['genre']} matches your favorite")
    else:
        reasons.append(f"✗ Genre: {song['genre']} (you prefer {user_prefs['favorite_genre']})")
    
    # Mood match (30%)
    mood_weight = 0.30
    mood_match = 1.0 if song['mood'].lower() == user_prefs['favorite_mood'].lower() else 0.0
    score_components['mood'] = mood_match * mood_weight
    if mood_match == 1.0:
        reasons.append(f"✓ Mood match: {song['mood']} matches your favorite")
    else:
        reasons.append(f"✗ Mood: {song['mood']} (you prefer {user_prefs['favorite_mood']})")
    
    # Energy match (20%)
    energy_weight = 0.20
    energy_diff = abs(float(song['energy']) - user_prefs['target_energy'])
    energy_match = max(0.0, 1.0 - energy_diff)  # Closer to target = higher score
    score_components['energy'] = energy_match * energy_weight
    reasons.append(f"⚡ Energy: {float(song['energy']):.2f} (target: {user_prefs['target_energy']:.2f}, match: {energy_match:.2f})")
    
    # Other attributes - Valence and Acousticness (10%)
    other_weight = 0.10
    
    # Valence (positivity): prefer higher if user likes energetic music, lower for chill
    valence_score = float(song['valence'])
    
    # Acousticness: use user preference
    acousticness_score = float(song['acousticness']) if user_prefs['likes_acoustic'] else (1.0 - float(song['acousticness']))
    
    other_match = (valence_score + acousticness_score) / 2.0
    score_components['other'] = other_match * other_weight
    
    acoustic_pref = "acoustic" if user_prefs['likes_acoustic'] else "electric/produced"
    reasons.append(f"🎨 Acousticness: {float(song['acousticness']):.2f} (you prefer {acoustic_pref})")
    
    # Calculate total weighted score
    total_score = sum(score_components.values())
    
    return total_score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score all songs and return top k recommendations sorted by score with reasoning."""
    # Score all songs
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, reasons))
    
    # Sort by score descending and return top k
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    return scored_songs[:k]
