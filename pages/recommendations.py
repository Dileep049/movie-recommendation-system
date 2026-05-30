import streamlit as st
import pandas as pd
import pickle

# =========================
# LOGIN CHECK
# =========================

if not st.session_state.get("logged_in", False):
    st.switch_page("web.py")

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Recommendations",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_movies():

    movies = pd.read_csv(
        "data/tmdb_5000_movies.csv"
    )

    telugu = pd.read_csv(
        "data/telugu_movies_10000.csv"
    )

    movies["language"] = "english"
    telugu["language"] = "telugu"

    combined = pd.concat(
        [movies, telugu],
        ignore_index=True
    )

    return combined


@st.cache_data
def load_posters():

    return pd.read_csv(
        "data/movie_posters.csv"
    )


movies = load_movies()
posters = load_posters()

similarity = pickle.load(
    open(
        "data/similarity.pkl",
        "rb"
    )
)

# =========================
# FUNCTIONS
# =========================

def get_poster(movie_name):

    try:

        movie = posters[
            posters["title"].str.lower()
            ==
            movie_name.lower()
        ]

        if len(movie):
            return movie.iloc[0]["poster"]

    except:
        pass

    return (
        "https://via.placeholder.com/"
        "300x450?text=No+Poster"
    )


def get_trailer(movie_name):

    movie_name = movie_name.replace(
        " ",
        "+"
    )

    return (
        f"https://www.youtube.com/results?"
        f"search_query={movie_name}+official+trailer"
    )


def recommend(movie_name):

    movie_index = movies[
        movies["title"] == movie_name
    ].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for movie in movie_list:

        recommendations.append(
            movies.iloc[movie[0]].title
        )

    return recommendations

# =========================
# TITLE
# =========================

st.title("🔥 Recommended Movies")

selected_movie = st.session_state.get(
    "selected_movie",
    ""
)

if selected_movie == "":

    st.warning(
        "Select a movie first"
    )

    st.stop()

st.info(
    f"Recommendations based on: {selected_movie}"
)

# =========================
# SHOW RECOMMENDATIONS
# =========================

recommendations = recommend(
    selected_movie
)

cols = st.columns(5)

for i, movie in enumerate(
    recommendations
):

    with cols[i]:

        st.image(
            get_poster(movie),
            use_container_width=True
        )

        st.write(movie)

        st.link_button(
            "▶ Trailer",
            get_trailer(movie),
            key=f"trailer_{i}"
        )

        if st.button(
            "❤️ Save",
            key=f"fav_{i}"
        ):

            if (
                "favorites"
                not in st.session_state
            ):
                st.session_state.favorites = []

            if movie not in st.session_state.favorites:

                st.session_state.favorites.append(
                    movie
                )

                st.success(
                    "Added"
                )

# =========================
# NEXT PAGE
# =========================

st.write("---")

if st.button(
    "❤️ View Favorites",
    use_container_width=True
):

    st.switch_page(
        "pages/favorites.py"
    )

if st.button(
    "⬅ Back To Details",
    use_container_width=True
):

    st.switch_page(
        "pages/details.py"
    )