import streamlit as st
import pandas as pd
import os

# =========================
# LOGIN CHECK
# =========================
if not st.session_state.get("logged_in", False):
    st.switch_page("web.py")

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Home",
    layout="wide"
)

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp{
    background: linear-gradient(
        135deg,
        #090909 0%,
        #111827 35%,
        #1e1b4b 100%
    );
}

.hero{
    text-align:center;
    padding:60px 20px;
}

.hero h1{
    color:white;
    font-size:70px;
    font-weight:800;
}

.hero p{
    color:#cbd5e1;
    font-size:22px;
}

.movie-card{
    background:rgba(255,255,255,0.05);
    padding:15px;
    border-radius:20px;
    transition:0.4s;
}

.movie-card:hover{
    transform:translateY(-10px);
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA FUNCTIONS
# =========================
@st.cache_data
def load_movies():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    eng_path = os.path.join(base_dir, "data", "tmdb_5000_movies.csv")
    tel_path = os.path.join(base_dir, "data", "telugu_movies_10000.csv")

    eng = pd.read_csv(eng_path)
    tel = pd.read_csv(tel_path)

    eng["language"] = "english"
    tel["language"] = "telugu"

    # Dataset runtime cleaning numbers context remove loop
    if "title" in tel.columns:
        tel["title"] = tel["title"].astype(str).str.replace(r'\s*\d+$', '', regex=True)

    movies_combined = pd.concat([eng, tel], ignore_index=True)
    return movies_combined

@st.cache_data
def load_posters():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posters_path = os.path.join(base_dir, "data", "movie_posters.csv")
    return pd.read_csv(posters_path)

# Data Variables Call setup
movies = load_movies()
posters = load_posters()

# =========================
# LANGUAGE SELECTOR
# =========================
language = st.sidebar.selectbox(
    "🌐 Select Language",
    ["english", "telugu"]
)

st.session_state.language = language

filtered_movies = movies[
    movies["language"] == language
]

# =========================
# POSTER FUNCTION
# =========================
def get_poster(movie_name):
    movie_name_str = str(movie_name).strip().lower()
    posters["title"] = posters["title"].astype(str)
    
    movie = posters[
        posters["title"].str.strip().str.lower()
        ==
        movie_name_str
    ]

    if len(movie) > 0:
        return movie.iloc[0]["poster"]

    return "https://via.placeholder.com/300x450?text=No+Poster"

# =========================
# HERO SECTION
# =========================
st.markdown("""
<div class="hero">
<h1>🎬 CineMind AI</h1>
<p>
Discover Movies • Watch Trailers • Get AI Recommendations
</p>
</div>
""", unsafe_allow_html=True)

# =========================
# NAVIGATION BUTTONS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Home", use_container_width="stretch", key="nav_home_btn"):
        st.switch_page("pages/home.py")

with col2:
    if st.button("🔍 Search", use_container_width="stretch", key="nav_search_btn"):
        st.switch_page("pages/search.py")

with col3:
    if st.button("🔥 Recommendations", use_container_width="stretch", key="nav_recs_btn"):
        st.switch_page("pages/recommendations.py")

with col4:
    if st.button("❤️ Favorites", use_container_width="stretch", key="nav_fav_btn"):
        st.switch_page("pages/favorites.py")

st.write("---")

# =========================
# START BUTTON
# =========================
if st.button(
    "🚀 Start Exploring Movies",
    use_container_width="stretch",
    key="start_explore_main_btn"
):
    st.switch_page("pages/search.py")

st.write("")

# =========================
# TRENDING
# =========================
st.subheader("🔥 Trending Movies")

if len(filtered_movies) > 0:
    trending = filtered_movies.sample(
        min(5, len(filtered_movies)),
        random_state=42 # Stable loading rules setup
    )

    cols = st.columns(5)

    for i, movie in enumerate(trending.itertuples()):
        with cols[i % 5]:
            st.image(
                get_poster(movie.title),
                use_container_width="stretch"
            )
            st.write(movie.title)

            if st.button(
                "View Details",
                key=f"trending_movie_btn_{i}"
            ):
                st.session_state.selected_movie = movie.title
                st.switch_page("pages/details.py")
else:
    st.info("No movie listings found for this segment.")

# =========================
# TOP RATED
# =========================
st.write("")
st.subheader("⭐ Top Rated Movies")

if len(filtered_movies) > 0:
    if "vote_average" not in filtered_movies.columns:
        filtered_movies["vote_average"] = 8.0
        
    top = filtered_movies.sort_values(
        by="vote_average",
        ascending=False
    ).head(5)

    cols2 = st.columns(5)

    for i, movie in enumerate(top.itertuples()):
        with cols2[i % 5]:
            st.image(
                get_poster(movie.title),
                use_container_width="stretch"
            )
            st.write(movie.title)
            st.write(f"⭐ {round(movie.vote_average, 1)}")

            if st.button(
                "Open Details",
                key=f"top_rated_movie_btn_{i}"
            ):
                st.session_state.selected_movie = movie.title
                st.switch_page("pages/details.py")

# =========================
# QUICK ACTIONS
# =========================
st.write("")
st.subheader("⚡ Quick Actions")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🔍 Search Engine Gateway", key="home_nav_search_unique_btn"):
        st.switch_page("pages/search.py")

with c2:
    if st.button("🔥 Recommendations Engine", key="home_nav_recs_unique_btn"):
        st.switch_page("pages/recommendations.py")

with c3:
    if st.button("❤️ Favorites List", key="home_nav_favs_unique_btn"):
        st.switch_page("pages/favorites.py")

# =========================
# FOOTER
# =========================
st.write("---")
username_display = st.session_state.get('username', 'Guest')
st.caption(f"👤 Logged in as: {username_display}")
st.caption("Developed by Dileep 🚀")