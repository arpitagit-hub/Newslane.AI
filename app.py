import streamlit as st
from openai import OpenAI
import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="StreamNewsAI", layout="wide")

client = OpenAI(api_key="sk-xxxxxxxxxxxx")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_news" not in st.session_state:
    st.session_state.selected_news = None

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("## 📰 StreamNewsAI")

with col2:
    nav1, nav2, nav3, nav4 = st.columns(4)

    with nav1:
        if st.button("Home"):
            st.session_state.page = "home"

    with nav2:
        if st.button("Sources"):
            st.session_state.page = "sources"

    with nav3:
        if st.button("About"):
            st.session_state.page = "about"

    with nav4:
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
        else:
            if st.button("Login"):
                st.session_state.logged_in = True

st.markdown("---")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Dashboard")

    menu = st.radio(
        "Navigate",
        ["📊 Dashboard", "📰 Current News", "🤖 AI Query"]
    )

# ---------------- HOME ----------------
if st.session_state.page == "home":

    st.markdown("### 🔍 Filter News")

    col1, col2 = st.columns(2)

    with col1:
        source = st.selectbox(
            "Select Source",
            ["All", "TV9 Bangla", "ABP News", "Anandabazar"]
        )

    with col2:
        date = st.date_input("Select Date", datetime.date.today())

    st.markdown("---")
    st.markdown("## 📰 Latest News")

    news_list = [
        {"title": "Kolkata Weather Update", "source": "TV9 Bangla", "desc": "Heavy rain expected."},
        {"title": "Election Update", "source": "ABP News", "desc": "New updates in WB politics."},
        {"title": "Stock Market", "source": "Anandabazar", "desc": "Market rising today."},
    ]

    cols = st.columns(3)

    for i, news in enumerate(news_list):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h4>{news['title']}</h4>
                <p><b>{news['source']}</b></p>
                <p>{news['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open News {i}"):
                st.session_state.selected_news = news

    # ---------------- NEWS DETAIL ----------------
    if st.session_state.selected_news:

        news = st.session_state.selected_news

        st.markdown("---")
        st.markdown("## 📰 News Details")

        st.markdown(f"### {news['title']}")
        st.write(f"📌 Source: {news['source']}")
        st.write(news['desc'])

        # 🔍 Previous News
        st.markdown("### 📅 See Previous News")

        selected_date = st.date_input("Select Date for previous news")

        if st.button("Load Previous News"):
            st.info(f"Showing news for {selected_date}")

        # 🤖 Summarize
        if st.button("Summarize News"):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Summarize this news: {news['desc']}"
                }]
            )

            st.success(response.choices[0].message.content)

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
    - Filters by source & date
    - Provides AI insights

    🚀 Built by Arpita
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