import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Movie Details",
    layout="wide"
)

# =========================
# LOGIN CHECK
# =========================
if not st.session_state.get("logged_in", False):
    st.switch_page("web.py")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_movies():

    movies = pd.read_csv("data/tmdb_5000_movies.csv")
    telugu = pd.read_csv("data/telugu_movies_10000.csv")

    movies["language"] = "english"
    telugu["language"] = "telugu"

    return pd.concat(
        [movies, telugu],
        ignore_index=True
    )


@st.cache_data
def load_posters():

    return pd.read_csv(
        "data/movie_posters.csv"
    )


movies = load_movies()
posters = load_posters()

# =========================
# FUNCTIONS
# =========================
def get_poster(movie_name):

    try:
        movie = posters[
            posters["title"].astype(str).str.lower()
            ==
            movie_name.lower()
        ]

        if len(movie) > 0:

            poster = movie.iloc[0]["poster"]

            if pd.notna(poster):
                return poster

    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Poster"


def get_trailer(movie_name):

    query = movie_name.replace(" ", "+")

    return (
        f"https://www.youtube.com/results?"
        f"search_query={query}+official+trailer"
    )

# =========================
# GET SELECTED MOVIE
# =========================
movie_name = st.session_state.get(
    "selected_movie",
    ""
)

if movie_name == "":

    st.warning("⚠️ Select a movie first")

    if st.button("⬅ Back"):
        st.switch_page("pages/search.py")

    st.stop()

# =========================
# FETCH MOVIE
# =========================
movie_data = movies[
    movies["title"] == movie_name
]

if len(movie_data) == 0:

    st.error("Movie Not Found")
    st.stop()

movie = movie_data.iloc[0]

# =========================
# PAGE TITLE
# =========================
st.title("🎬 Movie Details")

# =========================
# MOVIE SECTION
# =========================
col1, col2 = st.columns([1, 2])

with col1:

    st.image(
        get_poster(movie_name),
        use_container_width=True
    )

with col2:

    st.subheader(movie_name)

    rating = movie.get("vote_average", 0)

    if pd.isna(rating):
        rating = 0

    rating = float(rating)

    st.write(
        f"⭐ Rating: {rating}/10"
    )

    st.progress(
        max(
            0.0,
            min(rating / 10, 1.0)
        )
    )

    st.write("### 📖 Overview")

    overview = movie.get(
        "overview",
        "No overview available"
    )

    st.info(overview)

# =========================
# TRAILER
# =========================
st.write("---")

st.link_button(
    "▶️ Watch Trailer",
    get_trailer(movie_name),
    use_container_width=True
)

# =========================
# FAVORITES
# =========================
if st.button(
    "❤️ Add To Favorites",
    use_container_width=True
):

    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    if movie_name not in st.session_state.favorites:

        st.session_state.favorites.append(
            movie_name
        )

        st.success(
            "Added To Favorites"
        )

    else:

        st.info(
            "Already In Favorites"
        )

# =========================
# NAVIGATION
# =========================
st.write("---")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "⬅ Back To Search",
        use_container_width=True
    ):
        st.switch_page(
            "pages/search.py"
        )

with col2:

    if st.button(
        "🔥 Recommendations",
        use_container_width=True
    ):
        st.switch_page(
            "pages/recommendations.py"
        )