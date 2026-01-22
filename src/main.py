import pandas as pd
import requests
from collections import Counter
from pathlib import Path

API_KEY = "d86d402b52408716263ed356f871511c"
BASE_URL = "https://api.themoviedb.org/3"
TARGET_USER_ID = 611

def safe_request(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {}

def fetch_movie_details(movie_id):
    data = safe_request(f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}")
    return data.get('title', f"Unknown Movie ({movie_id})"), data.get('vote_average', 0)

def get_super_fan_recommendations(target_user_id, ratings_df):
    print(f"\n🕵️‍♂️  Analyzing profile for User {target_user_id}...")
    
    user_history = ratings_df[
        (ratings_df['userId'] == target_user_id) & 
        (ratings_df['rating'] >= 4.0)
    ]
    
    if user_history.empty:
        print("❌ Insufficient data. User has no highly rated movies.")
        return []

    my_movie_ids = user_history['movieId'].tolist()
    print(f"ℹ️  Found {len(my_movie_ids)} liked movies in history. Scanning database...")

    fans = ratings_df[
        (ratings_df['movieId'].isin(my_movie_ids)) & 
        (ratings_df['rating'] >= 4.5) & 
        (ratings_df['userId'] != target_user_id)
    ]
    
    if fans.empty:
        print("⚠️ No 'Super-Fans' found matching this taste profile.")
        return []
        
    print(f"✅ {len(fans)} 'Super-Fans' identified. Aggregating data...")

    top_fan_ids = fans['userId'].value_counts().head(10).index.tolist()
    
    recommended_pool = []
    for fan_id in top_fan_ids:
        fan_favs = ratings_df[
            (ratings_df['userId'] == fan_id) & 
            (ratings_df['rating'] >= 4.5) & 
            (~ratings_df['movieId'].isin(my_movie_ids))
        ]['movieId'].tolist()
        recommended_pool.extend(fan_favs)

    top_recs = Counter(recommended_pool).most_common(10)
    
    return top_recs

def run():
    print("--- 🚀 Movie Guru SERG: Super-Fan Engine CLI ---")
    
    try:
        ratings = pd.read_csv("data/ratings.csv")
    except FileNotFoundError:
        try:
            ratings = pd.read_csv("../data/ratings.csv")
        except FileNotFoundError:
            print("ERROR: 'ratings.csv' not found in data directory.")
            return

    recommendations = get_super_fan_recommendations(TARGET_USER_ID, ratings)

    if recommendations:
        print("\n✨ TOP RECOMMENDATIONS (Collaborative Filtering Results):")
        print("-" * 60)
        for i, (movie_id, count) in enumerate(recommendations):
            title, score = fetch_movie_details(movie_id)
            print(f"{i+1}. {title} \n   (Endorsed by {count} Super-Fans | TMDB: {score})")
            print("-" * 60)
    else:
        print("\n😔 No sufficient patterns found to generate recommendations.")

if __name__ == "__main__":
    run()