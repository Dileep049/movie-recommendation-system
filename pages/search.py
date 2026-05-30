import streamlit as st
import pandas as pd
import speech_recognition as sr

# =========================
# LOGIN CHECK
# =========================

if not st.session_state.get("logged_in", False):
    st.switch_page("web.py")

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Search Movies",
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

    combined["title"] = combined["title"].astype(str)

    return combined

movies = load_movies()

# =========================
# LANGUAGE SELECTOR
# =========================

language = st.sidebar.selectbox(
    "🌐 Language",
    ["english", "telugu"]
)

st.session_state.language = language

# =========================
# FILTER MOVIES
# =========================

filtered_movies = movies[
    movies["language"] == language
]

movie_list = filtered_movies[
    "title"
].astype(str).tolist()

# =========================
# DEBUG
# =========================

st.sidebar.success(
    f"Movies Loaded: {len(filtered_movies)}"
)

# =========================
# TITLE
# =========================

st.title("🔍 Search Movies")

st.write(
    "Search your favourite movie"
)

st.write("---")

# =========================
# SEARCH BOX
# =========================

search_text = st.text_input(
    "🎬 Enter Movie Name"
)

# DEBUG OUTPUT

st.write(
    "Total Telugu Movies:",
    len(
        movies[
            movies["language"] == "telugu"
        ]
    )
)

st.write(
    movies[
        movies["language"] == "telugu"
    ]["title"].head(20)
)

if search_text:

    results = [

        movie

        for movie in movie_list

        if search_text.lower().strip()

        in str(movie).lower().strip()
    ]

    st.write(
        "Results Found:",
        len(results)
    )

    if len(results) > 0:

        selected_movie = st.selectbox(
            "Results",
            results
        )

        st.session_state.selected_movie = (
            selected_movie
        )

    else:

        st.warning(
            "No movie found"
        )

# =========================
# VOICE SEARCH
# =========================

st.write("---")

if st.button(
    "🎤 Voice Search",
    use_container_width=True
):

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            st.info(
                "Speak Movie Name..."
            )

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source
            )

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        st.success(
            f"Recognized: {text}"
        )

        voice_results = [

            movie

            for movie in movie_list

            if text.lower()

            in str(movie).lower()
        ]

        if len(voice_results) > 0:

            st.session_state.selected_movie = (
                voice_results[0]
            )

            st.success(
                f"Selected: {voice_results[0]}"
            )

        else:

            st.warning(
                "Movie not found"
            )

    except Exception as e:

        st.error(
            f"Voice Search Failed: {e}"
        )

# =========================
# VIEW DETAILS
# =========================

st.write("---")

if st.button(
    "🎬 View Movie Details",
    use_container_width=True
):

    if st.session_state.get(
        "selected_movie",
        ""
    ):

        st.switch_page(
            "pages/details.py"
        )

    else:

        st.warning(
            "Select a movie first"
        )

# =========================
# BACK BUTTON
# =========================

if st.button(
    "⬅ Back To Home",
    use_container_width=True
):

    st.switch_page(
        "pages/home.py"
    )