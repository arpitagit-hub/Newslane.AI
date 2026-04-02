import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import datetime
import requests

load_dotenv()

# ---------------- CONFIG ----------------
st.set_page_config(page_title="StreamNewsAI", layout="wide")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_channel" not in st.session_state:
    st.session_state.selected_channel = None

# 🔥 NEW USER SESSION
if "user" not in st.session_state:
    st.session_state.user = None

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("## 📰 StreamNewsAI")

with col2:
    nav1, nav2, nav3, nav4 = st.columns(4)

    if nav1.button("Home"):
        st.session_state.page = "home"

    if nav2.button("Sources"):
        st.session_state.page = "sources"

    if nav3.button("About"):
        st.session_state.page = "about"

    if st.session_state.logged_in:
        if nav4.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
    else:
        if nav4.button("Login"):
            st.session_state.page = "login"

st.markdown("---")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Dashboard")

    menu = st.radio(
        "Navigate",
        ["📊 Dashboard", "📰 Current News", "🤖 AI Query"]
    )

    # 🔥 PROFILE SECTION
    if st.session_state.logged_in and st.session_state.user:
        st.markdown("## 👤 Profile")
        user = st.session_state.user
        st.write(f"Name: {user['name']}")
        st.write(f"Email: {user['email']}")
        st.write(f"Password: {user['password']}")

        st.markdown("### ⭐ Favorites")
        for fav in st.session_state.favorites:
            st.write(f"✔ {fav}")

# ---------------- LOGIN PAGE ----------------
if st.session_state.page == "login":

    st.markdown("## 🔐 Login")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login Now"):
        if name and email and password:
            st.session_state.user = {
                "name": name,
                "email": email,
                "password": password
            }
            st.session_state.logged_in = True
            st.success("Logged in successfully ✅")
            st.session_state.page = "home"
        else:
            st.error("Please fill all fields")

# ---------------- HOME ----------------
elif st.session_state.page == "home":

    st.markdown("## 📰 News Channels")

    channels = [
        "TV9 Bangla",
        "ABP Ananda",
        "Anandabazar",
        "Zee 24 Ghanta",
        "Kolkata News"
    ]

    cols = st.columns(3)

    for i, ch in enumerate(channels):
        with cols[i % 3]:

            st.markdown(f"""
            <div class="card">
                <h4>{ch}</h4>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Get News from {ch}"):
                st.session_state.selected_channel = ch

            # ⭐ FAVORITE BUTTON
            if st.button(f"⭐ {ch}"):
                if ch not in st.session_state.favorites:
                    st.session_state.favorites.append(ch)

    # 🔒 DATE ACCESS CONTROL
    if not st.session_state.logged_in:
        st.info("Login to access previous news")
        selected_date = datetime.date.today()
    else:
        selected_date = st.date_input("Select Date", datetime.date.today())

    channel_query_map = {
        "TV9 Bangla": "Kolkata weather OR West Bengal news",
        "ABP Ananda": "West Bengal politics OR Kolkata news",
        "Anandabazar": "West Bengal news",
        "Zee 24 Ghanta": "India news OR Kolkata",
        "Kolkata News": "Kolkata latest news"
    }

    if st.session_state.selected_channel:

        channel = st.session_state.selected_channel

        st.markdown(f"## 📰 News from {channel}")

        query = channel_query_map.get(channel, "Kolkata news")

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": query,
            "from": str(datetime.date.today() - datetime.timedelta(days=1)),
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": NEWS_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "articles" in data and len(data["articles"]) > 0:

            article = data["articles"][0]

            st.markdown(f"### {article['title']}")
            st.write(article.get("description", ""))

            content = article.get("content", "No content available")

            expand_prompt = f"""
            Expand this into a detailed news report (500-1000 words):

            {content}
            """

            try:
                expanded = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": expand_prompt}]
                )
                full_report = expanded.choices[0].message.content
            except Exception:
                full_report = content
                st.warning("⚠️ Showing basic report (AI limit reached)")

            st.write(full_report)

            # 🔒 SUMMARY ACCESS CONTROL
            if not st.session_state.logged_in:
                st.warning("🔒 Login to use AI summarization")
            else:
                st.markdown("### 🧠 Choose Summary Type")

            mode = st.selectbox("Select Summary Type", [
                "Brief Summary",
                "Short Summary",
                "Deep Summary",
                "60 Sec Summary"
            ])

            if st.button("Summarize"):

                if mode == "Brief Summary":
                    prompt = f"Summarize in 2 lines:\n{full_report}"
                elif mode == "Short Summary":
                    prompt = f"Summarize in 5 lines:\n{full_report}"
                elif mode == "Deep Summary":
                    prompt = f"Give detailed summary:\n{full_report}"
                else:
                    prompt = f"Explain like 60-second speech:\n{full_report}"

                try:
                    summary = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}]
                )
                    st.success(summary.choices[0].message.content)

                except Exception:
                    st.warning("⚠️ AI limit reached → Showing basic summary")

            # 👇 THIS IS NEW
                    st.write(full_report[:300] + "...")

# ---------------- SOURCES ----------------
elif st.session_state.page == "sources":

    st.markdown("## 📰 News Sources")

    sources = ["TV9 Bangla", "ABP News", "Anandabazar"]

    for s in sources:
        if st.button(s):
            st.success(f"Showing news from {s}")

# ---------------- ABOUT ----------------
elif st.session_state.page == "about":

    st.markdown("""
    ## ℹ️ About StreamNewsAI

    AI-powered news platform that:
    - Summarizes news
    """)

# ---------------- SIDEBAR FEATURES ----------------
if menu == "🤖 AI Query":

    st.markdown("## 🤖 Ask AI")

    q = st.text_input("Ask about news")

    if st.button("Ask"):
        if q:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": q}]
            )
            st.write(response.choices[0].message.content)

elif menu == "📊 Dashboard":
    st.info("Dashboard analytics coming soon 🚀")

elif menu == "📰 Current News":
    st.info("Live news integration coming soon 🔥")