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

    # Define multiple user preference profiles
    users = [
        {
            "name": "Alex (Pop Energy Lover)",
            "prefs": {
                "favorite_genre": "pop",
                "favorite_mood": "happy",
                "target_energy": 0.8,
                "likes_acoustic": False
            }
        },
        {
            "name": "Jordan (Chill Lofi Listener)",
            "prefs": {
                "favorite_genre": "lofi",
                "favorite_mood": "chill",
                "target_energy": 0.4,
                "likes_acoustic": True
            }
        },
        {
            "name": "Casey (Rock Intensity Seeker)",
            "prefs": {
                "favorite_genre": "rock",
                "favorite_mood": "intense",
                "target_energy": 0.9,
                "likes_acoustic": False
            }
        }
    ]

    # Generate recommendations for each user
    for user in users:
        name = user["name"]
        user_prefs = user["prefs"]
        
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\n" + "="*60)
        print(f"🎵 Recommendations for {name}")
        print("="*60)
        print(f"Preferences: {user_prefs['favorite_genre']} music with {user_prefs['favorite_mood']} mood (energy: {user_prefs['target_energy']:.1f})\n")
        
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
