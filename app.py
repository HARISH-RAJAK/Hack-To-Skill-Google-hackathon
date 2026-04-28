# Dae.Anuj

import streamlit as st
import cv2
import time
import pandas as pd

from controller import AdaptiveController, DIRECTIONS
from detector import detect_once

st.set_page_config(layout="wide")

# -------------------------
# 🎨 UI STYLE
# -------------------------
st.markdown("""
<style>
.main {background-color:#0e1117;}
.card {
padding:15px;
border-radius:15px;
background:#1c1f26;
text-align:center;
}
.green {color:#00ff88;}
.yellow {color:#ffcc00;}
.red {color:#ff4b4b;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 🧠 HEADER
# -------------------------
st.title("🚦 Smart Adaptive Traffic System")

# -------------------------
# ⚙️ SIDEBAR
# -------------------------
st.sidebar.header("Controls")

base_time = st.sidebar.slider("Base Round Time", 40, 120, 60)
min_green = st.sidebar.slider("Min Green", 5, 20, 8)
max_green = st.sidebar.slider("Max Green", 20, 60, 40)

# -------------------------
# 🧠 SESSION INIT
# -------------------------
if "caps" not in st.session_state:
    paths = {
        "North": "videos/North.mp4",
        "East": "videos/East.mp4",
        "South": "videos/South.mp4",
        "West": "videos/West.mp4"
    }
    
    # Check if videos exist
    caps = {}
    missing_videos = []
    
    for d in DIRECTIONS:
        try:
            cap = cv2.VideoCapture(paths[d])
            if not cap.isOpened():
                missing_videos.append(d)
                cap.release()
            else:
                caps[d] = cap
        except Exception as e:
            missing_videos.append(d)
    
    if missing_videos:
        st.error(f"⚠️ Missing video files: {', '.join(missing_videos)}")
        st.info("📌 **To deploy on Render/Streamlit Cloud:**\n1. Upload video files to `videos/` folder\n2. Push to GitHub\n3. Deploy again")
        st.stop()
    
    st.session_state.caps = caps

if "controller" not in st.session_state:
    st.session_state.controller = AdaptiveController(
        base_time, min_green, max_green
    )

if "scores" not in st.session_state:
    st.session_state.scores = {d: 0 for d in DIRECTIONS}

if "history" not in st.session_state:
    st.session_state.history = []

caps = st.session_state.caps
controller = st.session_state.controller

# -------------------------
# 🚀 NEW ROUND
# -------------------------
if not controller.round_active:
    st.session_state.scores = detect_once(caps)
    controller.start_round(st.session_state.scores)

    # Store history
    st.session_state.history.append(st.session_state.scores.copy())

scores = st.session_state.scores

# -------------------------
# 🔄 UPDATE SIGNAL
# -------------------------
lane, state, timer = controller.update()

# -------------------------
# 📂 TABS
# -------------------------
tab1, tab2 = st.tabs(["🚦 Signal View", "📊 Analytics"])

# =========================
# 🚦 SIGNAL VIEW
# =========================
with tab1:

    st.subheader("🚦 Live Signal Status")

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='card'>🚗 Lane<br><h2>{lane}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>🚦 State<br><h2 class='{state.lower()}'>{state}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>⏱ Timer<br><h2>{timer}</h2></div>", unsafe_allow_html=True)

    st.divider()

    colA, colB = st.columns(2)

    layout = {
        "North": colA,
        "East": colB,
        "South": colA,
        "West": colB
    }

    for d in DIRECTIONS:

        cap = caps[d]
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        if ret:
            frame = cv2.resize(frame, (400, 250))

            if d == lane:
                if state == "GREEN":
                    color = (0, 255, 0)
                elif state == "YELLOW":
                    color = (0, 255, 255)
                else:
                    color = (0, 0, 255)
            else:
                color = (80, 80, 80)

            cv2.rectangle(frame, (0, 0), (400, 250), color, 5)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            layout[d].image(frame, caption=f"{d}")

# =========================
# 📊 ANALYTICS VIEW
# =========================
with tab2:

    st.subheader("📊 Traffic Analysis")

    cols = st.columns(4)
    total = 0

    for i, d in enumerate(DIRECTIONS):
        g = controller.green_times[d]
        total += g

        cols[i].markdown(f"""
        <div class='card'>
        <b>{d}</b><br>
        🚗 Vehicles: {scores[d]}<br>
        ⏱ Green: {round(g,1)} sec
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div class='card'>⏱ Total Round: {round(total,1)} sec</div>", unsafe_allow_html=True)

    st.divider()

    # 📈 GRAPH SECTION
    st.subheader("📈 Traffic Trends")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)

        st.line_chart(df)

        st.subheader("📊 Current Traffic Distribution")

        latest = df.iloc[-1]
        st.bar_chart(latest)

    st.divider()

    st.subheader("🧠 Logic")

    st.code("""
Green Time ∝ Traffic Density

Constraints:
- Minimum Green Time
- Maximum Green Time
- Normalized Total Time
""")

# -------------------------
# 🔁 ROUND COMPLETE
# -------------------------
if lane == "ROUND_DONE":
    st.success("✅ Round Completed")

# -------------------------
# 🔄 LOOP
# -------------------------
time.sleep(1)
st.rerun()