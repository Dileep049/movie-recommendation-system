import streamlit as st
import pandas as pd

# =========================
# LOGIN CHECK
# =========================

if not st.session_state.get("logged_in", False):
    st.switch_page("web.py")

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Favorites",
    layout="wide"
)

# =========================
# LOAD POSTERS
# =========================

@st.cache_data
def load_posters():

    return pd.read_csv(
        "data/movie_posters.csv"
    )

posters = load_posters()

# =========================
# FAVORITES SESSION
# =========================

if "favorites" not in st.session_state:

    st.session_state.favorites = []

# =========================
# POSTER FUNCTION
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

.title{
    text-align:center;
    color:white;
    font-size:50px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.markdown(
    '<p class="title">❤️ My Favorites</p>',
    unsafe_allow_html=True
)

# =========================
# NO FAVORITES
# =========================

if len(st.session_state.favorites) == 0:

    st.warning(
        "No Favorite Movies Added Yet"
    )

    if st.button(
        "🔍 Search Movies",
        use_container_width=True
    ):

        st.switch_page(
            "pages/search.py"
        )

    st.stop()

# =========================
# FAVORITES GRID
# =========================

favorites = list(
    set(st.session_state.favorites)
)

for start in range(
    0,
    len(favorites),
    5
):

    cols = st.columns(5)

    row_movies = favorites[
        start:start+5
    ]

    for idx, movie in enumerate(
        row_movies
    ):

        with cols[idx]:

            st.image(
                get_poster(movie),
                use_container_width=True
            )

            st.write(movie)

            if st.button(
                "🎬 Details",
                key=f"details_{movie}"
            ):

                st.session_state.selected_movie = movie

                st.switch_page(
                    "pages/details.py"
                )

            if st.button(
                "❌ Remove",
                key=f"remove_{movie}"
            ):

                st.session_state.favorites.remove(
                    movie
                )

                st.rerun()

# =========================
# QUICK ACTIONS
# =========================

st.write("---")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):

        st.switch_page(
            "pages/home.py"
        )

with col2:

    if st.button(
        "🔍 Search",
        use_container_width=True
    ):

        st.switch_page(
            "pages/search.py"
        )

with col3:

    if st.button(
        "🔥 Recommendations",
        use_container_width=True
    ):

        st.switch_page(
            "pages/recommendations.py"
        )

# =========================
# FOOTER
# =========================

st.write("---")

st.caption(
    f"👤 {st.session_state.username}"
)

st.caption(
    "Developed by Dileep 🚀"
)