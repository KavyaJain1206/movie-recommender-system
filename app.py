import pickle
import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Movie Recommender")

# --- Constants ---
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
BASE_POSTER_URL = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750?text=No+Image"

# --- Load Data Safely ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, 'movies.pkl'), 'rb') as f:
        movies_data = pickle.load(f)

    if isinstance(movies_data, pd.DataFrame):
        movies = movies_data
    elif isinstance(movies_data, (dict, list)):
        movies = pd.DataFrame(movies_data)
    else:
        raise ValueError("Invalid format for movies.pkl")

    with open(os.path.join(BASE_DIR, 'similarity.pkl'), 'rb') as f:
        similarity = pickle.load(f)

except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# --- Poster Fetching ---
@st.cache_data(show_spinner=False, ttl=86400)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            poster_path = response.json().get("poster_path")
            if poster_path:
                return f"{BASE_POSTER_URL}/{poster_path}"
        else:
            print(f"TMDb API error ({response.status_code}) for ID {movie_id}")
    except Exception as e:
        print(f"Poster fetch error for ID {movie_id}: {e}")
    return PLACEHOLDER_POSTER

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_poster_by_title(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results and results[0].get("poster_path"):
                return f"{BASE_POSTER_URL}/{results[0]['poster_path']}"
    except Exception as e:
        print(f"Fallback poster search error for '{title}': {e}")
    return PLACEHOLDER_POSTER

# --- Recommendation Function ---
def recommend(movie_title):
    try:
        index = movies[movies['title'] == movie_title].index[0]
        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]

        recommended_names = []
        recommended_posters = []

        for i in distances:
            movie_id = movies.iloc[i[0]].movie_id
            title = movies.iloc[i[0]].title
            poster = fetch_poster(movie_id)
            if "placeholder" in poster:
                poster = fetch_poster_by_title(title)
            recommended_names.append(title)
            recommended_posters.append(poster)

        return recommended_names, recommended_posters

    except Exception as e:
        st.error(f"⚠️ Recommendation error: {e}")
        return [], []

# --- UI ---
st.title("🎬 Movie Recommender System")

if 'title' in movies.columns and not movies.empty:
    selected_movie = st.selectbox("🎥 Type or select a movie", movies['title'].values)
else:
    st.error("Missing 'title' column in movie data.")
    st.stop()

st.markdown("---")

if st.button("🔍 Show Recommendations"):
    names, posters = recommend(selected_movie)
    if names and posters:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx])
                st.caption(names[idx])
    else:
        st.warning("No recommendations found.")
