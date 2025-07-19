import pickle
import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="Movie Recommender")

# --- Helper Functions ---

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            else:
                print(f"No poster_path for movie ID: {movie_id}")
        else:
            print(f"TMDb API failed with status {response.status_code} for movie ID {movie_id}")
    except Exception as e:
        print(f"Exception fetching poster for {movie_id}: {e}")
    return "https://via.placeholder.com/500x750?text=No+Image"

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_poster_by_title(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key=8265bd1679663a7ea12ac168da84d2e8&query={title}"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results and results[0].get('poster_path'):
                return f"https://image.tmdb.org/t/p/w500/{results[0]['poster_path']}"
    except Exception as e:
        print(f"Fallback title search failed for '{title}': {e}")
    return "https://via.placeholder.com/500x750?text=No+Image"

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
        st.error(f"Recommendation error: {e}")
        return [], []

# --- Load Data ---

try:
    with open('movies.pkl', 'rb') as f:
        movies_data = pickle.load(f)

    if isinstance(movies_data, pd.DataFrame):
        movies = movies_data
    elif isinstance(movies_data, (dict, list)):
        movies = pd.DataFrame(movies_data)
    else:
        raise ValueError("Invalid format for movies.pkl")

    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)

except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# --- UI ---

st.title("🎬 Movie Recommender System")

if 'title' in movies.columns and not movies.empty:
    selected_movie = st.selectbox("🎥 Type or select a movie", movies['title'].values)
else:
    st.error("Missing 'title' column in movie data.")
    st.stop()

st.markdown("---")

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)
    if names and posters:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx])
                st.caption(names[idx])
    else:
        st.warning("No recommendations found.")
