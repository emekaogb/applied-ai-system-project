# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

- The features I would use in my recommender system would iclude genre, mood, energy, and valence. I think danceability could also be useful for contextualizing the listening experience (workout vs relaxation), but is not as important as the others. Using artist could limit discovery so I don't want it to focus too heavily on that. 
- UserProfile would store liked/disliked songs and listening history, along with the pre-existing info like favorite genre and favorite mood. 
- The Recommender computes a score for each song using cosine similarity, and creates recommendations using a ranking rule (ex. basic sorting).
- Algorithm Recipe: For each song, genre match is weighted 40%, mood match 30%, energy match 25%, and other attributes 10%. This system may over-prioritize genre but this is fine for a new user, and then weight can be adjusted later on. The scores that meet the given threshold will then be ranked by score (sorted descending) and the system would return the top K songs + scores. 

## Demo
![Recommender screenshot](demo/music_recommender_demo.png)
---
<img src="demo/alex_rec.png" alt="User1 screenshot" width="32%" /> <img src="demo/jordan_rec.png" alt="User2 screenshot" width="32%" /> <img src="demo/casey_rec.png" alt="User3 screenshot" width="32%" />

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Model Card (Reflection)

# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Cryosonic 1.0**  

---

## 2. Intended Use  

This generates personalized music recommendations by matching songs to a user's preferred genre, mood, and energy level from a curated catalog. It assumes users have stable taste preferences, without contradictions or unusual preference combinations. This is a classroom exploration tool designed to teach recommender system design principles, not for real-world deployment.

---

## 3. How the Model Works  

The system scores each song by checking how well it matches what you're looking for. Favorite genre gets 40% weight, preferred mood gets 30%, and how close the song's energy is to target energy gets 20%, with the remaining 10% based on how acoustic or produced you like your music. For example, a pop song with a happy mood that matches a user's high energy target would score much higher than a heavy metal song, even if the metal song has interesting qualities.

---

## 4. Data  

The catalog contains 20 songs spanning 16 distinct genres (pop, rock, lofi, ambient, jazz, country, metal, hip-hop, folk, classical, electronic, synthwave, r&b, reggae, indie pop, and punk) with moods ranging from chill and peaceful to intense and energetic. I did not add or remove any songs from the original dataset, the recommender uses the complete catalog provided for the simulation. Some important aspects of musical taste are missing, like lyrical themes and/or release era, which means the system can't understand temporal context in music.

---

## 5. Strengths  

The system works exceptionally well for users with straightforward preferences who have a clear favorite genre and mood that exist in the dataset. It correctly captures the intuition that genre and mood are the primary drivers of taste, and the weighted scoring system validates this by consistently ranking exact genre-mood-energy matches at the top. The transparent scoring approach also makes recommendations easy to explain and understand, which is crucial for building user trust.

---

## 6. Limitations and Bias 

The system uses a binary genre and mood matching, where it scores 0 if there isn't an eaxct match. This could be better, because there are genre and moods that may be similar but not exactly the same. Especially because genre and mood make up such a large percentage of the scoring rubric, this would be something to focus on for future iterations. Another limitation is that the system doesn't detect when a user's preferences contradict each other. For example, an intense lofi enjoyer should be rare, but if a user is recorded as such, the algorithm will produce confusing/inconsistent rankings without questioning the validity of these preferences. 

---

## 7. Evaluation  

I tested the system against 3 adversarial user profiles including edge cases like whitespace in genre names, out-of-range energy values, empty preferences, and contradictory combinations. I looked for whether recommendations remained consistent, scores stayed within logical bounds, and whether the system gracefully handled invalid inputs. What surprised me most was how severely the binary genre/mood matching degraded recommendations. The system also revealed that tied scores caused unpredictable ranking outcomes with no secondary sorting criteria. Most concerningly, contradictory preferences were silently accepted.

---

## 8. Future Work  

I would implement fuzzy matching for genres and moods so that similar, but not exact, preferences (like "rock" matching "indie rock") still receive appropriate credit instead of zero points. I'd also add input validation to detect and warn users when their preferences contradict each other, plus introduce a secondary tie-breaking criterion (like tempo) to ensure deterministic rankings. Finally, incorporating artist diversity or introducing randomization to the top results would help users discover new music beyond their exact preferences like in Spotify's Discover Weekly.

---

## 9. Personal Reflection  

I learned recommender systems have many layers, consisting of scoring rules, ranking rules, and more. Also, these systems typically use a variety of methods like content-based filtering and collaboritive filtering. This changed the way I think about music recommendation apps like Spotify compared to Apple Music, and also how I view other recommendation engines in use by platforms like Youtube, Netflix, and TikTok.
