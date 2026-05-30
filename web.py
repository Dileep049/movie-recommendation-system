import numpy as np
import streamlit as st
import pandas as pd
import speech_recognition as sr
import sqlite3
import pyttsx3
import pickle
import hashlib
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
conn = sqlite3.connect("database/users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites(
    username TEXT,
    movie TEXT
)
""")
conn.commit()

# ==========================================
# SESSION STATE MANAGEMENT
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "HOME"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "registered_user" not in st.session_state:
    st.session_state.registered_user = None
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "english"

# ==========================================
# HASHING UTILITIES
# ==========================================
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# ==========================================
# VOICE SYNTHESIS ENGINE
# ==========================================
@st.cache_resource
def get_voice_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except:
        return None

engine = get_voice_engine()

def speak(text):
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass

# ==========================================
# SCREEN CORES & THEME DEFINITIONS
# ==========================================
theme = st.sidebar.toggle("🌙 Dark Mode", value=True)
if theme:
    bg_color = "linear-gradient(135deg, #090909 0%, #111827 35%, #1e1b4b 100%)"
    text_color = "white"
else:
    bg_color = "white"
    text_color = "black"

# ==========================================
# ADVANCED CUSTOM CSS INJECTION
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}
.stApp {{
    background: {bg_color};
    color: {text_color};
}}
h1 {{
    text-align: center;
    font-size: 4rem !important;
    font-weight: 800 !important;
    color: white !important;
}}
.login-box {{
    background: rgba(255,255,255,0.06);
    padding: 40px;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(20px);
    margin-top: 20px;
}}
.stButton > button {{
    width: 100%;
    background: linear-gradient(90deg, #9333ea, #ec4899);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 12px;
    font-size: 16px;
    font-weight: 700;
    transition: all 0.3s ease;
}}
.stButton > button:hover {{
    transform: translateY(-3px);
}}
.active-tab-btn > button {{
    background: linear-gradient(90deg, #6366f1, #4f46e5) !important;
    border: 1px solid #818cf8 !important;
}}
.inactive-tab-btn > button {{
    background: rgba(255, 255, 255, 0.05) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}}
.nav-active-block > button {{
    background: linear-gradient(90deg, #ec4899, #f43f5e) !important;
    border: 1px solid #f43f5e !important;
}}
.nav-inactive-block > button {{
    background: rgba(255, 255, 255, 0.03) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}}
img {{
    border-radius: 15px;
}}
.movie-card {{
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 20px;
    transition: 0.4s;
}}
.movie-card:hover {{
    transform: scale(1.05) translateY(-10px);
    box-shadow: 0px 10px 30px rgba(236,72,153,0.4);
}}
footer {{
    visibility: hidden;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA PROCESSING PIPELINE
# ==========================================
@st.cache_data
def load_data():
    movies_df = pd.read_csv("data/tmdb_5000_movies.csv")
    movies_df["language"] = "english"

    telugu_movies_df = pd.read_csv("data/telugu_movies_10000.csv")
    telugu_movies_df["language"] = "telugu"
    
    if "vote_average" not in telugu_movies_df.columns:
        telugu_movies_df["vote_average"] = 8.0

    combined_df = pd.concat([movies_df, telugu_movies_df], ignore_index=True)
    combined_df = combined_df[["title", "overview", "vote_average", "language"]]
    combined_df.dropna(inplace=True)
    combined_df.drop_duplicates(subset="title", inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    poster_df = pd.read_csv("data/movie_posters.csv")
    return combined_df, poster_df

movies, poster_data = load_data()

# ==========================================
# SAFE SIMILARITY PROCESSING MATRICES
# ==========================================
@st.cache_data
def generate_runtime_similarity(dataframe):
    # Enforces exact similarity space allocation mapping sequentially over dataset limits
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vector_matrix = cv.fit_transform(dataframe["overview"])
    return cosine_similarity(vector_matrix)

# Safety Fallback: Checks pickle framework arrays boundary constraint issues dynamically
try:
    similarity_pickle = pickle.load(open("data/similarity.pkl", "rb"))
    if len(similarity_pickle) < len(movies):
        similarity_pickle = generate_runtime_similarity(movies)
except:
    similarity_pickle = generate_runtime_similarity(movies)

# ==========================================
# SYSTEM FUNCTION HELPER ARRAYS
# ==========================================
def get_poster(movie_name):
    movie_name = str(movie_name).strip().lower()
    poster_data["title"] = poster_data["title"].astype(str)
    movie = poster_data[poster_data["title"].str.strip().str.lower() == movie_name]
    if len(movie) > 0:
        return movie.iloc[0]["poster"]
    return "https://via.placeholder.com/300x450?text=No+Poster"

def get_trailer(movie_name):
    search_query = movie_name.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={search_query}+official+trailer"

def recommend(movie_title, selected_language):
    matched = movies[movies["title"].str.lower() == movie_title.lower()]
    if len(matched) == 0:
        return []

    movie_index = matched.index[0]
    
    # CRITICAL SECURITY COMPENSATOR: Dynamic vector processing validation bypasses IndexError
    if movie_index >= len(similarity_pickle):
        cv_runtime = CountVectorizer(max_features=5000, stop_words="english")
        vector_runtime = cv_runtime.fit_transform(movies["overview"])
        target_vector = vector_runtime[movie_index]
        distances = cosine_similarity(target_vector, vector_runtime).flatten()
    else:
        distances = similarity_pickle[movie_index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:50]
    recommended_movies = []
    
    for i in movies_list:
        movie = movies.iloc[i[0]]
        if movie["language"] == selected_language and movie["title"].lower() != movie_title.lower():
            recommended_movies.append(movie["title"])
        if len(recommended_movies) == 5:
            break
            
    return recommended_movies

# ==========================================
# GATEWAY AUTHORIZATION MODALS
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1>🎬 CineMind AI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            login_btn_class = "active-tab-btn" if st.session_state.auth_mode == "login" else "inactive-tab-btn"
            st.markdown(f'<div class="{login_btn_class}">', unsafe_allow_html=True)
            if st.button("🔐 Login", key="gateway_tab_login_trigger"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with btn_col2:
            register_btn_class = "active-tab-btn" if st.session_state.auth_mode == "register" else "inactive-tab-btn"
            st.markdown(f'<div class="{register_btn_class}">', unsafe_allow_html=True)
            if st.button("📝 Register", key="gateway_tab_register_trigger"):
                st.session_state.auth_mode = "register"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "login":
            st.subheader("Account Authorization Login")
            username_input = st.text_input("Username", key="auth_field_login_user").strip()
            password_input = st.text_input("Password", type="password", key="auth_field_login_pass")
            st.write("")
            if st.button("Sign In Entry", key="action_trigger_execute_login"):
                if username_input and password_input:
                    cursor.execute("SELECT password FROM users WHERE username=?", (username_input,))
                    data = cursor.fetchone()
                    if data and check_hashes(password_input, data[0]):
                        st.session_state.logged_in = True
                        st.session_state.username = username_input
                        st.session_state.page = "HOME"
                        st.success("✅ Login Successful")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials")
                else:
                    st.warning("⚠️ Input fields cannot remain empty space.")
        else:
            st.subheader("Create New Profile Registration")
            reg_username = st.text_input("Choose Username", key="auth_field_reg_user").strip()
            reg_password = st.text_input("Choose Password", type="password", key="auth_field_reg_pass")
            st.write("")
            if st.button("Execute Profile Creation", key="action_trigger_execute_register"):
                if reg_username and reg_password:
                    cursor.execute("SELECT username FROM users WHERE username=?", (reg_username,))
                    existing_user = cursor.fetchone()
                    if existing_user:
                        st.error("⚠️ Username already taken! Select a different key.")
                    else:
                        hashed_password = make_hashes(reg_password)
                        cursor.execute("INSERT INTO users VALUES(?,?)", (reg_username, hashed_password))
                        conn.commit()
                        st.session_state.registered_user = {
                            "username": reg_username,
                            "password": reg_password
                        }
                        st.success("🎉 Registration Confirmed Successfully!")
                else:
                    st.warning("⚠️ Input fields cannot remain empty space.")

            if st.session_state.registered_user is not None:
                st.write("")
                st.info("ℹ️ **Newly Initialized Registration Credentials Saved:**")
                st.code(f"""👤 Created Username: {st.session_state.registered_user['username']}\n🔑 Saved Password : {st.session_state.registered_user['password']}""", language="text")
                if st.button("💡 Proceed Straight to Login Form", key="switch_back_to_login_after_reg"):
                    st.session_state.auth_mode = "login"
                    st.session_state.registered_user = None
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# LOGGED IN DASHBOARD CONTROL CENTRE
# ==========================================
else:
    st.markdown("<h1 style='margin-bottom:10px;'>🎬 CineMind AI</h1>", unsafe_allow_html=True)
    control_left, control_right = st.columns([4, 1])
    
    with control_left:
        selected_language = st.selectbox(
            "🌐 Select Content Interface Language",
            ["english", "telugu"],
            index=0 if st.session_state.selected_language == "english" else 1,
            key="dashboard_language_global_selector"
        )
        st.session_state.selected_language = selected_language

    with control_right:
        st.write("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="top_header_logout_trigger"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.auth_mode = "login"
            st.session_state.registered_user = None
            st.rerun()

    st.write("")

    # NAVIGATION TABS SYSTEM
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
    with nav_col1:
        h_class = "nav-active-block" if st.session_state.page == "HOME" else "nav-inactive-block"
        st.markdown(f'<div class="{h_class}">', unsafe_allow_html=True)
        if st.button("🏠 HOME", use_container_width=True, key="nav_to_home_panel"):
            st.session_state.page = "HOME"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_col2:
        s_class = "nav-active-block" if st.session_state.page == "SEARCH" else "nav-inactive-block"
        st.markdown(f'<div class="{s_class}">', unsafe_allow_html=True)
        if st.button("🔍 SEARCH", use_container_width=True, key="nav_to_search_panel"):
            st.session_state.page = "SEARCH"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_col3:
        d_class = "nav-active-block" if st.session_state.page == "MOVIE DETAILS" else "nav-inactive-block"
        st.markdown(f'<div class="{d_class}">', unsafe_allow_html=True)
        if st.button("🎬 DETAILS", use_container_width=True, key="nav_to_details_panel"):
            st.session_state.page = "MOVIE DETAILS"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_col4:
        r_class = "nav-active-block" if st.session_state.page == "RECOMMENDATIONS" else "nav-inactive-block"
        st.markdown(f'<div class="{r_class}">', unsafe_allow_html=True)
        if st.button("🔥 AI RECS", use_container_width=True, key="nav_to_recs_panel"):
            st.session_state.page = "RECOMMENDATIONS"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_col5:
        f_class = "nav-active-block" if st.session_state.page == "FAVORITES" else "nav-inactive-block"
        st.markdown(f'<div class="{f_class}">', unsafe_allow_html=True)
        if st.button("❤️ FAVORITES", use_container_width=True, key="nav_to_favs_panel"):
            st.session_state.page = "FAVORITES"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    filtered_movies = movies[movies["language"] == st.session_state.selected_language]
    movie_list = filtered_movies["title"].values

    # ------------------------------------------
    # 1. PAGE MODULE PANEL: HOME VIEW
    # ------------------------------------------
    if st.session_state.page == "HOME":
        st.subheader("🔥 Top Trending Movie Collections")
        if len(filtered_movies) > 0:
            trending_movies = filtered_movies.sample(min(5, len(filtered_movies)), random_state=42)
            cols = st.columns(5)
            for idx, row in enumerate(trending_movies.itertuples()):
                with cols[idx % 5]:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    st.image(get_poster(row.title), use_container_width=True)
                    st.markdown(f"<p style='min-height:45px; font-weight:500;'>{row.title}</p>", unsafe_allow_html=True)
                    if st.button("Inspect Film", key=f"action_home_select_mov_{idx}"):
                        st.session_state.selected_movie = row.title
                        st.session_state.page = "MOVIE DETAILS"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No movie rows available under this scope module selection.")

    # ------------------------------------------
    # 2. PAGE MODULE PANEL: SEARCH VIEW
    # ------------------------------------------
    elif st.session_state.page == "SEARCH":
        st.subheader("🔍 Movie Data Space Search Engine")
        search = st.text_input("Enter keywords matching target title library", key="search_bar_input_element")
        filtered_search = [movie for movie in movie_list if search.lower() in movie.lower()]

        if len(filtered_search) > 0:
            selected_movie = st.selectbox("Filter Dynamic Selection Matrix Results", filtered_search, key="search_engine_results_dropdown")
            st.session_state.selected_movie = selected_movie
            st.write("")
            if st.button("Open Selected Movie Profile Details", key="confirm_search_selection_switch"):
                st.session_state.page = "MOVIE DETAILS"
                st.rerun()
        else:
            st.error("No record matching criteria entries found.")

        st.write("---")
        if st.button("🎤 Activate Voice Recognition Interface Search", key="voice_recog_trigger_action"):
            recognizer = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    st.info("System Engine Listening... Speak Film Title Now:")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source)
                voice_text = recognizer.recognize_google(audio, language="en-IN")
                st.success(f"Speech Processed Result Token: {voice_text}")
            except:
                st.error("Voice Hardware Connection Error or Engine Interrupted.")

    # ------------------------------------------
    # 3. PAGE MODULE PANEL: MOVIE DETAILS VIEW
    # ------------------------------------------
    elif st.session_state.page == "MOVIE DETAILS":
        st.subheader("🎬 Targeted Movie Profile Dossier")
        movie = st.session_state.selected_movie
        
        if movie != "":
            # Search whole movies DataFrame to enable across-the-board metadata lookup safely
            movie_data = movies[movies["title"] == movie]
            if len(movie_data) > 0:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(get_poster(movie), use_container_width=True)
                with col2:
                    st.markdown(f"## {movie}")
                    rating = round(movie_data.iloc[0].vote_average, 1)
                    st.write(f"⭐ Global Rating Coefficient: {rating}/10")
                    st.progress(rating / 10)
                    st.info(movie_data.iloc[0].overview)
                    st.link_button("▶️ Stream Official Trailer Archive", get_trailer(movie))
                    st.write("")
                    if st.button("❤️ Save to Account Favorites Vault", key="add_to_favs_database_action"):
                        cursor.execute("INSERT INTO favorites VALUES(?,?)", (st.session_state.username, movie))
                        conn.commit()
                        st.success(f"✔️ Added '{movie}' to user directory profile archive.")
            else:
                st.warning("Selected movie properties metadata not structuralized for this configuration.")
        else:
            st.info("Please choose a movie from the HOME or SEARCH page first to look up details.")

    # ------------------------------------------
    # 4. PAGE MODULE PANEL: AI RECOMMENDATIONS VIEW
    # ------------------------------------------
    elif st.session_state.page == "RECOMMENDATIONS":
        st.subheader("🔥 AI Engine Nearest Neighbor Movie Predictions")
        movie = st.session_state.selected_movie
        
        if movie != "":
            st.write(f"Generating vectors matching relational map rules for: **{movie}**")
            recommendations = recommend(movie, st.session_state.selected_language)
            
            if len(recommendations) > 0:
                cols = st.columns(5)
                for idx, rec_movie in enumerate(recommendations):
                    with cols[idx % 5]:
                        st.markdown('<div class="movie-card" style="min-height:380px;">', unsafe_allow_html=True)
                        st.image(get_poster(rec_movie), use_container_width=True)
                        st.markdown(f"<p style='min-height:45px; font-size:14px; font-weight:500;'>{rec_movie}</p>", unsafe_allow_html=True)
                        
                        # Added instant inspector switch directly inside recommendation pipeline layout
                        if st.button("Inspect", key=f"rec_inspect_btn_{idx}"):
                            st.session_state.selected_movie = rec_movie
                            st.session_state.page = "MOVIE DETAILS"
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No similar movies found matching the active language setting.")
        else:
            st.info("No movie selected context target. Please choose a movie layout target first.")

    # ------------------------------------------
    # 5. PAGE MODULE PANEL: FAVORITES VAULT VIEW
    # ------------------------------------------
    elif st.session_state.page == "FAVORITES":
        st.subheader("❤️ User Secured Personal Favorites Directory")
        cursor.execute("SELECT movie FROM favorites WHERE username=?", (st.session_state.username,))
        favs = cursor.fetchall()
        
        if len(favs) > 0:
            unique_favs = list(set([f[0] for f in favs]))
            cols = st.columns(5)
            for idx, fav_movie in enumerate(unique_favs):
                with cols[idx % 5]:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    st.image(get_poster(fav_movie), use_container_width=True)
                    st.markdown(f"<p style='font-weight:500; min-height:40px;'>{fav_movie}</p>", unsafe_allow_html=True)
                    if st.button("View", key=f"fav_view_trigger_{idx}"):
                        st.session_state.selected_movie = fav_movie
                        st.session_state.page = "MOVIE DETAILS"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No records stored inside current profile local storage tables database.")

# ==========================================
# UNIVERSAL SYSTEM CONTAINER MARKUP FOOTER
# ==========================================
st.write("---")
if st.session_state.logged_in:
    st.caption(f"👤 Account User Tracking Token: {st.session_state.username}")
st.caption("Developed by Dileep 🚀")