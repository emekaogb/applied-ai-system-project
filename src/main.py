"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # User preference profile - matches the score_song algorithm
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n🎵 Top Music Recommendations\n")
    print(f"User preferences: {user_prefs['favorite_genre']} music with {user_prefs['favorite_mood']} mood\n")
    
    for i, rec in enumerate(recommendations, 1):
        song, score, reasons = rec
        print(f"{i}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} | Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"   Why recommended:")
        for reason in reasons:
            print(f"      {reason}")
        print()


if __name__ == "__main__":
    main()
