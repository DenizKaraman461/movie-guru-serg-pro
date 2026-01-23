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
    
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    
    div[data-testid="stImage"] img {
        width: auto !important;
        height: auto !important;
        max-height: 150px !important;
        max-width: 100% !important;  
        object-fit: contain !important;
        border-radius: 8px !important;
        margin: 0 auto !important;   
        transition: transform 0.2s;
    }
    div[data-testid="stImage"] img:hover { transform: scale(1.05); }

    div[data-baseweb="tab-list"] { 
        justify-content: center; 
        gap: 5px; 
        margin-bottom: 10px; 
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    div[data-baseweb="tab"] { 
        border-radius: 8px; 
        background-color: rgba(255,255,255,0.05); 
        padding: 5px 10px; 
        font-size: 0.8rem;
        white-space: nowrap;
        min-width: auto;
    }
    div[aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }

    @media (max-width: 768px) {
        div[data-testid="column"] {
            width: 33.33% !important;   
            flex: 0 0 33.33% !important;
            min-width: 33.33% !important;
            padding: 0 2px !important;  
        }
        
        div[data-testid="stMarkdown"] p, div[data-testid="stText"] {
            font-size: 0.7rem !important;
            line-height: 1.1 !important;
            text-align: center !important;
        }
        
        button[kind="secondary"], button[kind="primary"] {
            padding: 0px !important;
            font-size: 0.7rem !important;
            min-height: 25px !important;
            width: 100% !important;
        }
    }

    .scroll-container { display: flex; flex-direction: row; overflow-x: auto; gap: 10px; padding: 10px 0; scrollbar-width: none; }
    .scroll-container::-webkit-scrollbar { display: none; }
    .movie-card-scroll { flex: 0 0 100px; width: 100px; padding: 5px; display: flex; flex-direction: column; align-items: center; }
    .movie-card-scroll img { width: 100%; border-radius: 6px; aspect-ratio: 2/3; object-fit: cover; }
    .movie-title-scroll { font-size: 9px; color: #ccc; text-align: center; height: 25px; overflow: hidden; margin-top: 4px; line-height: 1.1; }
    .ticket-btn { width: 100%; background-color: #ff4b4b; color: white; padding: 2px 0; border-radius: 4px; font-size: 9px; text-align: center; text-decoration: none; margin-top: auto; display: block; }
    </style>
""", unsafe_allow_html=True)

def safe_request(url):
    try:
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return {}

def super_fan_recommendation(user_movies):
    try: ratings_df = pd.read_csv("data/ratings.csv")
    except: 
        try: ratings_df = pd.read_csv("../data/ratings.csv")
        except: return [], "DB Error"

    if not user_movies: return [], "No Data"
    my_movie_ids = [m['id'] for m in user_movies]
    last_genre = user_movies[-1].get('genre_ids', [28])[0]
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={last_genre}&sort_by=vote_average.desc&vote_count.gte=300"
    data = safe_request(url)
    return data.get('results', [])[:5], "Genre Match"

def fetch_search(query):
    data = safe_request(f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}")
    return data.get('results', [])[:12]

def fetch_popular():
    data = safe_request(f"{BASE_URL}/movie/popular?api_key={API_KEY}")
    return data.get('results', [])[:12]

def fetch_now_playing():
    data = safe_request(f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&region=TR")
    return data.get('results', [])

if 'my_movies' not in st.session_state: st.session_state.my_movies = []

st.title("🍿 𝖒𝖔𝖛𝖎𝖊 𝖌𝖚𝖗𝖚 𝖘𝖊𝖗𝖌 𝖕𝖗𝖔")
st.caption(f"User {USER_ID} | Intelligent Engine")
st.divider()

st.subheader("1. 𝖆𝖉𝖉 𝖋𝖆𝖛𝖔𝖗𝖎𝖙𝖊𝖘 ")
q = st.text_input("Search", placeholder="Film adı...", label_visibility="collapsed")

tab_explore, tab_results, tab_watchlist = st.tabs(["🌍 𝖊𝖝𝖕𝖑𝖔𝖗𝖊", "🔍 𝖗𝖊𝖘𝖚𝖑𝖙𝖘", "📝 𝖜𝖆𝖙𝖈𝖍𝖑𝖎𝖘𝖙"])

with tab_explore:
    pop = fetch_popular()
    cols = st.columns(6)
    for i, m in enumerate(pop):
        with cols[i%6]:
            if m.get('poster_path'): 
                st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
            if st.button("➕", key=f"p{m['id']}"):
                if not any(x['id']==m['id'] for x in st.session_state.my_movies):
                    st.session_state.my_movies.append({'id':m['id'], 'title':m['title'], 'poster':m.get('poster_path'), 'genre_ids':m.get('genre_ids',[])})
                    st.toast(f"Eklendi", icon="✅")

with tab_results:
    if q:
        res = fetch_search(q)
        if res:
            cols_res = st.columns(6)
            for i, m in enumerate(res):
                with cols_res[i%6]:
                    if m.get('poster_path'): 
                        st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
                    st.markdown(f"<div style='font-size:10px;text-align:center;white-space:nowrap;overflow:hidden;'>{m['title']}</div>", unsafe_allow_html=True)
                    if st.button("Add", key=f"s{m['id']}"):
                        if not any(x['id']==m['id'] for x in st.session_state.my_movies):
                            st.session_state.my_movies.append({'id':m['id'], 'title':m['title'], 'poster':m.get('poster_path'), 'genre_ids':m.get('genre_ids',[])})
                            st.toast("Eklendi", icon="✅")
        else:
            st.warning("Sonuç yok.")
    else:
        st.info("Arama yapın ⬆️")

with tab_watchlist:
    if st.session_state.my_movies:
        cols_w = st.columns(6)
        for i, m in enumerate(st.session_state.my_movies):
            with cols_w[i%6]:
                p = f"{IMAGE_BASE_URL}{m['poster']}" if m['poster'] else ""
                st.image(p, use_container_width=True)
                if st.button("❌ Sil", key=f"del{m['id']}", type="secondary"):
                    st.session_state.my_movies.pop(i)
                    st.rerun()

        st.divider()
        
        if st.button("🚀 𝖗𝖚𝖓 𝖊𝖓𝖌𝖎𝖓𝖊 ", type="primary", use_container_width=True):
            st.markdown("### 🧠 Guru Sonuçları")
            recs, reason = super_fan_recommendation(st.session_state.my_movies)
            st.caption(f"Logic: {reason}")
            
            if recs:
                rec_cols = st.columns(6)
                for i, m in enumerate(recs):
                    with rec_cols[i%6]:
                        st.image(f"{IMAGE_BASE_URL}{m.get('poster_path')}", use_container_width=True)
                        st.markdown(f"<div style='font-size:10px;text-align:center;'>{m['title']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:10px;text-align:center;color:#f1c40f;'>★ {m.get('vote_average')}</div>", unsafe_allow_html=True)
    else:
        st.info("Listeniz boş. Explore veya Results sekmelerinden film ekleyin.")

st.divider()

st.header("🎟️ 𝖎𝖓 𝖙𝖍𝖊𝖆𝖙𝖊𝖗𝖘 ")
now = fetch_now_playing()
if now:
    h = ""
    for m in now:
        t = m['title'].replace('"','&quot;')
        p = f"{IMAGE_BASE_URL}{m.get('poster_path')}" if m.get('poster_path') else ""
        link = f"https://www.google.com/search?q={t} showtimes Izmir"
        h += f"""<div class="movie-card-scroll"><img src="{p}"><div class="movie-title-scroll">{t}</div><a href="{link}" target="_blank" class="ticket-btn">Bilet</a></div>"""
    st.markdown(f'<div class="scroll-container">{h}</div>', unsafe_allow_html=True)