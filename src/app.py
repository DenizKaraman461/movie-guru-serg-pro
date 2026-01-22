import streamlit as st
import pandas as pd
import requests
from collections import Counter

API_KEY = "d86d402b52408716263ed356f871511c"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"
USER_ID = 611

st.set_page_config(page_title="Movie Guru SERG Pro", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0E1117; color: #E0E0E0; }
    
    div[data-testid="stImage"] img { border-radius: 8px; transition: transform 0.3s ease; }
    div[data-testid="stImage"] img:hover { transform: scale(1.05); z-index: 10; }

    .scroll-container { display: flex; flex-direction: row; overflow-x: auto; gap: 15px; padding: 20px 0; white-space: nowrap; }
    .scroll-container::-webkit-scrollbar { height: 8px; }
    .scroll-container::-webkit-scrollbar-thumb { background-color: #5E6AD2; border-radius: 4px; }
    
    .movie-card-scroll { flex: 0 0 150px; width: 150px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; align-items: center; }
    .movie-card-scroll img { width: 100%; border-radius: 8px; margin-bottom: 8px; aspect-ratio: 2/3; object-fit: cover; }
    .movie-title-scroll { font-size: 13px; font-weight: 600; color: white; white-space: normal; text-align: center; height: 35px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .ticket-btn { display: inline-block; width: 100%; background-color: #ff4b4b; color: white; text-decoration: none; padding: 5px 0; border-radius: 5px; font-size: 11px; font-weight: bold; text-align: center; margin-top: auto; }
    </style>
""", unsafe_allow_html=True)

def safe_request(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {}

def super_fan_recommendation(user_movies):
    try:
        ratings_df = pd.read_csv("data/ratings.csv")
    except:
        # Try parent directory if running from src
        try:
            ratings_df = pd.read_csv("../data/ratings.csv")
        except:
            return [], "Database Connection Error"

    if not user_movies:
        return [], "Insufficient Data"

    my_movie_ids = [m['id'] for m in user_movies]
    
    fans = ratings_df[
        (ratings_df['movieId'].isin(my_movie_ids)) & 
        (ratings_df['rating'] >= 4.5) & 
        (ratings_df['userId'] != USER_ID)
    ]

    if not fans.empty:
        top_fan_ids = fans['userId'].value_counts().head(10).index.tolist()
        
        recommended_movie_ids = []
        for fan_id in top_fan_ids:
            fan_favorites = ratings_df[
                (ratings_df['userId'] == fan_id) & 
                (ratings_df['rating'] >= 4.5) & 
                (~ratings_df['movieId'].isin(my_movie_ids))
            ]['movieId'].tolist()
            recommended_movie_ids.extend(fan_favorites)
        
        common_recommendations = [movie_id for movie_id, count in Counter(recommended_movie_ids).most_common(5)]
        
        final_recs = []
        for mid in common_recommendations:
            data = safe_request(f"{BASE_URL}/movie/{mid}?api_key={API_KEY}")
            if 'title' in data:
                final_recs.append(data)
                
        return final_recs, f"Analysis based on {len(my_movie_ids)} titles"

    else:
        last_genre = user_movies[-1].get('genre_ids', [28])[0]
        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={last_genre}&sort_by=vote_average.desc&vote_count.gte=1000"
        data = safe_request(url)
        candidates = data.get('results', [])[:5]
        return candidates, "Genre-based fallback"

def fetch_search(query):
    data = safe_request(f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}")
    return data.get('results', [])[:8]

def fetch_popular():
    data = safe_request(f"{BASE_URL}/movie/popular?api_key={API_KEY}")
    return data.get('results', [])[:6]

def fetch_now_playing():
    data = safe_request(f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&region=TR")
    return data.get('results', [])

def get_genres_txt(ids):
    map = {28:"Action", 12:"Adventure", 16:"Animation", 35:"Comedy", 80:"Crime", 99:"Doc", 18:"Drama", 10751:"Family", 14:"Fantasy", 36:"History", 27:"Horror", 10402:"Music", 9648:"Mystery", 10749:"Romance", 878:"Sci-Fi", 53:"Thriller", 10752:"War", 37:"Western"}
    return " • ".join([map.get(i,"") for i in ids[:2] if i in map])

def save_to_csv(movie_id, rating=5.0):
    try:
        path = "data/ratings.csv"
        # Check if file exists to handle header correctly or path issues
        new_data = pd.DataFrame([[USER_ID, movie_id, rating]], columns=['userId', 'movieId', 'rating'])
        try:
            new_data.to_csv(path, mode='a', header=False, index=False)
        except FileNotFoundError:
            new_data.to_csv("../data/ratings.csv", mode='a', header=False, index=False)
    except Exception:
        pass

if 'my_movies' not in st.session_state: st.session_state.my_movies = []

st.title("🎬 Movie Guru SERG Pro")
st.caption(f"User {USER_ID} | Guru Intelligence Engine")
st.divider()

c1, c2 = st.columns([1, 2], gap="large")
with c1:
    st.subheader("1. Add Favorites")
    q = st.text_input("Search...", placeholder="Movie name...")
    st.write("---")
    st.subheader("🔥 Quick Add")
    pop = fetch_popular()
    cols = st.columns(3)
    for i, m in enumerate(pop):
        with cols[i%3]:
            if m.get('poster_path'): st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
            if st.button("➕", key=f"p{m['id']}"):
                if not any(x['id']==m['id'] for x in st.session_state.my_movies):
                    st.session_state.my_movies.append({'id':m['id'], 'title':m['title'], 'poster':m.get('poster_path'), 'genre_ids':m.get('genre_ids',[])})
                    save_to_csv(m['id'])
                    st.toast(f"Added {m['title']}", icon="✅")
with c2:
    if q:
        st.subheader("Results")
        res = fetch_search(q)
        cols = st.columns(4)
        for i, m in enumerate(res):
            with cols[i%4]:
                if m.get('poster_path'): st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
                st.markdown(f"<div style='font-size:12px;font-weight:bold;white-space:nowrap;overflow:hidden;'>{m['title']}</div>", unsafe_allow_html=True)
                if st.button("Add", key=f"s{m['id']}", use_container_width=True):
                    if not any(x['id']==m['id'] for x in st.session_state.my_movies):
                        st.session_state.my_movies.append({'id':m['id'], 'title':m['title'], 'poster':m.get('poster_path'), 'genre_ids':m.get('genre_ids',[])})
                        save_to_csv(m['id'])
                        st.toast("Added!", icon="✅")

st.divider()

st.subheader("2. Your Watchlist")
if st.session_state.my_movies:
    cols = st.columns(8)
    for i, m in enumerate(st.session_state.my_movies):
        with cols[i%8]:
            if m['poster']: st.image(f"{IMAGE_BASE_URL}{m['poster']}", use_container_width=True)
            if st.button("❌", key=f"d{m['id']}"):
                st.session_state.my_movies.pop(i)
                st.rerun()
else: st.info("Add movies to activate the recommendation engine.")

st.divider()

if st.button("🚀 RUN ENGINE", type="primary", use_container_width=True):
    c_off, c_on = st.columns(2, gap="large")
    
    with c_off:
        st.header("🧠 Guru Intelligence")
        if st.session_state.my_movies:
            
            recs, reason = super_fan_recommendation(st.session_state.my_movies)
            st.caption(f"Logic: {reason}")
            
            if recs:
                for i, m in enumerate(recs):
                    with st.container():
                        cc1, cc2 = st.columns([1, 3])
                        with cc1: st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
                        with cc2:
                            st.subheader(f"{i+1}. {m['title']}")
                            st.markdown(f"<small>{get_genres_txt(m.get('genre_ids',[]))}</small>", unsafe_allow_html=True)
                            st.write(f"⭐ {m.get('vote_average')}")
            else:
                st.warning("Insufficient data patterns found.")
        else:
            st.warning("Add a movie first.")

    with c_on:
        st.header("🌐 Standard AI")
        st.caption("Standard Similar Movies")
        if st.session_state.my_movies:
            last = st.session_state.my_movies[-1]['id']
            url = f"{BASE_URL}/movie/{last}/recommendations?api_key={API_KEY}"
            data = safe_request(url)
            api_recs = data.get('results', [])[:5]
            for m in api_recs:
                with st.container():
                    cc1, cc2 = st.columns([1, 3])
                    with cc1: st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
                    with cc2:
                        st.subheader(m['title'])
                        st.markdown(f"<small>{get_genres_txt(m.get('genre_ids',[]))}</small>", unsafe_allow_html=True)
                        st.write(f"⭐ {m.get('vote_average')}")

st.divider()

st.header("🎟️ In Theaters")
now = fetch_now_playing()
if now:
    h = ""
    for m in now:
        t = m['title'].replace('"','&quot;')
        p = f"{IMAGE_BASE_URL}{m.get('poster_path')}" if m.get('poster_path') else ""
        link = f"https://www.google.com/search?q={t} showtimes Izmir"
        h += f"""<div class="movie-card-scroll"><img src="{p}"><div class="movie-title-scroll" title="{t}">{t}</div><a href="{link}" target="_blank" class="ticket-btn">Tickets</a></div>"""
    st.markdown(f'<div class="scroll-container">{h}</div>', unsafe_allow_html=True)