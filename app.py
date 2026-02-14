import os
import json
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# Get PIN securely from secrets
try:
    PIN = str(st.secrets["PIN"])
except Exception:
    PIN = "2808"  # fallback for local testing

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Ren's Valentine Portal",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Helpers
# -----------------------------
def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback

def list_photos(folder="assets/photos"):
    exts = (".png", ".jpg", ".jpeg", ".webp")
    if not os.path.isdir(folder):
        return []
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
    files.sort()
    return files

def inject_css():
    st.markdown(
        """
        <style>
        /* Background + general typography */
        .stApp {
          background: radial-gradient(circle at 10% 10%, #FFE4E6 0%, #FFF1F2 35%, #FFFFFF 120%);
        }
        /* Floating heart background */
        .hearts-bg {
          position: fixed;
          inset: 0;
          z-index: 0;
          pointer-events: none;
          opacity: 0.16;
          background-image:
            radial-gradient(circle at 10% 20%, rgba(225,29,72,0.25) 0 2px, transparent 3px),
            radial-gradient(circle at 70% 15%, rgba(225,29,72,0.20) 0 2px, transparent 3px),
            radial-gradient(circle at 25% 75%, rgba(225,29,72,0.18) 0 2px, transparent 3px),
            radial-gradient(circle at 80% 70%, rgba(225,29,72,0.22) 0 2px, transparent 3px);
          background-size: 220px 220px, 260px 260px, 240px 240px, 280px 280px;
          background-repeat: repeat;
          filter: blur(0.2px);
        }
        /* Bring Streamlit content above bg */
        section.main > div { position: relative; z-index: 1; }

        /* Cute header */
        .hero {
          background: linear-gradient(135deg, #FFFFFF 0%, #FFF1F2 65%, #FFE4E6 100%);
          border: 1px solid rgba(225,29,72,0.15);
          border-radius: 22px;
          padding: 20px 18px;
          box-shadow: 0 10px 30px rgba(17,24,39,0.06);
          margin-bottom: 14px;
        }
        .hero h1 {
          margin: 0 0 6px 0;
          font-size: 34px;
          line-height: 1.12;
          letter-spacing: -0.6px;
        }
        .subtitle {
          margin: 0;
          font-size: 15px;
          opacity: 0.85;
        }
        .pillrow { margin-top: 12px; display:flex; gap:8px; flex-wrap:wrap; }
        .pill {
          display:inline-block;
          padding: 6px 10px;
          border-radius: 999px;
          background: #FFFFFF;
          border: 1px solid rgba(225,29,72,0.18);
          font-size: 13px;
        }

        /* Card */
        .card {
          background: #FFFFFF;
          border: 1px solid rgba(225,29,72,0.14);
          border-radius: 18px;
          padding: 14px 14px;
          box-shadow: 0 10px 25px rgba(17,24,39,0.05);
          margin: 10px 0;
        }
        .card h3 { margin: 0 0 8px 0; font-size: 18px; }
        .muted { opacity: 0.75; font-size: 13px; }

        /* Buttons: more romantic */
        div.stButton > button {
          border-radius: 14px !important;
          padding: 10px 14px !important;
          border: 1px solid rgba(225,29,72,0.22) !important;
          box-shadow: 0 10px 20px rgba(225,29,72,0.08);
        }
        /* Premium flashcard styling (Open-When letters) */
        .flashcard {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF1F2 70%, #FFE4E6 100%);
        border: 1px solid rgba(225,29,72,0.16);
        border-radius: 22px;
        padding: 16px 16px;
        box-shadow: 0 14px 30px rgba(17,24,39,0.06);
        margin: 10px 0;
        }

        .flashcard.open {
        background: #FFFFFF;
        }

        .flashcard-title {
        font-size: 16px;
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.2px;
        }

        .flashcard-hint {
        font-size: 12.5px;
        opacity: 0.75;
        margin: 0;
        }

        .flashcard-body p {
        margin: 0 0 10px 0;
        line-height: 1.5;
        }

        </style>
        <div class="hearts-bg"></div>
        """,
        unsafe_allow_html=True
    )

def card(title, body_html):
    st.markdown(
        f"""
        <div class="card">
          <h3>{title}</h3>
          <div>{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# State
# -----------------------------

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = False

if "valentine_answer" not in st.session_state:
    st.session_state.valentine_answer = None

PAGES = ["Home", "Photos", "Timeline", "Letters", "Quiz", "Valentine"]

if "page" not in st.session_state:
    st.session_state.page = 0  # 0..5

if "last_page" not in st.session_state:
    st.session_state.last_page = None
# ---- Balloons on every page change ----
if "last_page" not in st.session_state:
    st.session_state.last_page = None

if st.session_state.last_page != st.session_state.page:
    st.balloons()
    st.session_state.last_page = st.session_state.page


# flashcard flip states will be created dynamically for letters

def go(delta):
    st.session_state.page = max(0, min(len(PAGES) - 1, st.session_state.page + delta))
    st.experimental_rerun()

def jump(i):
    st.session_state.page = i
    st.experimental_rerun()

# -----------------------------
# Load data
# -----------------------------
timeline = load_json("data/timeline.json", [])
letters = load_json("data/letters.json", [])
quiz = load_json("data/quiz.json", [])

# -----------------------------
# UI
# -----------------------------
inject_css()

# ---- Gate / PIN ----
if not st.session_state.unlocked:
    st.markdown(
        """
        <div class="hero">
          <h1>💌 Ren’s Valentine Portal</h1>
          <p class="subtitle">corny, cringey, and a tiny bit of chaos — just like us.</p>
          <div class="pillrow">
            <span class="pill">Our eyes only ;)</span>
            <span class="pill">💗 Cute mode: ON</span>
            <span class="pill">🔐 PIN locked</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        card(
            "Enter the secret PIN",
            "because all treasures worth something are well guarded ;)"
        )
        pin_try = st.text_input(
            "Enter the secret PIN",
            type="password",
            placeholder="Hint: the date we became official 🥹"
        )

        if st.button("Unlock (if you dare)"):
            if pin_try.strip() == PIN:
                st.session_state.unlocked = True
                st.experimental_rerun()
            else:
                st.error("Nope 😭 Try again, bebi.")

        st.caption("Tip: On mobile, rotate if you want bigger photos.")

    st.stop()

# ---- Top navigation (no changes to your existing UI wording below) ----
colL, colM, colR = st.columns([1, 2, 1])
with colL:
    if st.button("⬅ Back", disabled=st.session_state.page == 0):
        go(-1)
with colR:
    if st.button("Next ➡", disabled=st.session_state.page == len(PAGES) - 1):
        go(+1)

tabs = st.columns(6)
for i, name in enumerate(PAGES):
    with tabs[i]:
        if st.button(name):
            jump(i)

# -----------------------------
# PAGES
# -----------------------------

# PAGE 0 — Home
if st.session_state.page == 0:
    st.markdown(
        """
        <div class="hero">
          <h1>Hi, Ren!</h1>
          <p class="subtitle">Welcome to your little Valentine corner on the internet. Scroll slowly…I made this with love!</p>
          <div class="pillrow">
            <span class="pill">Our Very First Valentine's day</span>
            <span class="pill">I love you sooooooo much!!</span>
            <span class="pill">💌 A digital love letter for you</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    card(
        "A tiny love note 🥹",
        """
        Ren, you’re my favorite person. The one who makes ordinary days feel like a scene from a romcom.
        Thank you for being yourself: soft, funny, handsome, and most importantly all mine (heheheh).  
        <br><br>
        Now go explore your portal like the main character you are, kween 💋
        """
    )

# PAGE 1 — Photos
elif st.session_state.page == 1:
    photos = list_photos("assets/photos")
    card(
        "Photo Wall 📸",
        "A little trot down the memory lane ;)"
    )

    if photos:
        cols = st.columns(3)
        captions = [
            "us >>>", "my favorite view", "cutest human", "pretty boy alert",
            "this one’s illegal", "we ate", "we smiled", "we slayed",
            "my heart", "forever vibe"
        ]
        for i, p in enumerate(photos[:10]):
            with cols[i % 3]:
                try:
                    img = ImageOps.exif_transpose(Image.open(p))
                    st.image(img, use_column_width=True)
                    st.caption(captions[i] if i < len(captions) else "💗")
                except Exception:
                    st.image(p, use_column_width=True)
    else:
        st.info("Add your photos to `assets/photos/` (01.jpg, 02.jpg, …). The wall will appear here 💗")

# PAGE 2 — Timeline
elif st.session_state.page == 2:
    st.markdown("### Our Timeline 🗓️💞")
    for item in timeline:
        date = item.get("date", "")
        title = item.get("title", "")
        line = item.get("line", "")
        card(
            f"{date} — {title}",
            f"<p style='margin:0;'>{line}</p>"
        )

# PAGE 3 — Letters (flash cards)
elif st.session_state.page == 3:
    st.markdown("### Open-When Letters 💌")
    st.caption("Pick one. Read it slowly. Pretend I’m right there.")

    # init flip states
    for i in range(len(letters)):
        k = f"letter_flip_{i}"
        if k not in st.session_state:
            st.session_state[k] = False

    cols = st.columns(2)

    for i, letter in enumerate(letters):
        title = letter.get("title", "Open")
        body = letter.get("body", [])

        with cols[i % 2]:
            is_open = st.session_state[f"letter_flip_{i}"]

            st.markdown(
                f"""
                <div class="flashcard {'open' if is_open else ''}">
                  <div class="flashcard-title">{title}</div>
                  <div class="flashcard-hint">
                    {"Tap again to close" if is_open else "Tap to open 💌"}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if not is_open:
                if st.button("Open 💌", key=f"open_{i}", use_container_width=True):
                    st.session_state[f"letter_flip_{i}"] = True
                    st.experimental_rerun()
            else:
                st.markdown('<div class="card flashcard-body">', unsafe_allow_html=True)
                for para in body:
                    st.write(para)
                st.markdown("</div>", unsafe_allow_html=True)

                if st.button("Close", key=f"close_{i}", use_container_width=True):
                    st.session_state[f"letter_flip_{i}"] = False
                    st.experimental_rerun()


# PAGE 4 — Quiz
elif st.session_state.page == 4:
    st.markdown("### Love Quiz")
    st.caption("No pressure. But also…yes pressure")

    if not quiz:
        st.warning("Your quiz file is empty. Add questions to `data/quiz.json`.")
    else:
        with st.form("quiz_form"):
            answers = []
            for idx, item in enumerate(quiz):
                q = item["q"]
                opts = item["options"]

                st.markdown(f"**Q{idx+1}. {q}**")

                choice = st.radio(
                    label=f"q{idx}",
                    options=["— Select an answer —"] + opts,
                    index=0,
                    label_visibility="collapsed"
                )
                answers.append(None if choice == "— Select an answer —" else choice)

            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            correct = 0
            total = len(quiz)

            for user_ans, item in zip(answers, quiz):
                if user_ans is not None and user_ans == item["answer"]:
                    correct += 1

            score_pct = int((correct / total) * 100)

            if correct == total:
                st.success(f"PERFECT SCORE: {correct}/{total} 💯💗")
            elif correct >= total - 1:
                st.success(f"Okayyyy smarty: {correct}/{total} 🌹")
            else:
                st.info(f"You got {correct}/{total} 😭 It’s okay, you’re still my favorite.")

            st.progress(score_pct)
            st.session_state.quiz_done = True

# PAGE 5 — Valentine
elif st.session_state.page == 5:
    st.markdown("### One Final Question")
    card(
        "Will you be my Valentine, bebi?",
        "Choose wisely (like your life depends on it)."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes 💗"):
            st.session_state.valentine_answer = "Yes"
            st.balloons()
            st.experimental_rerun()
    with col2:
        if st.button("Definitely Yes 😭💘"):
            st.session_state.valentine_answer = "Definitely Yes"
            st.balloons()
            st.experimental_rerun()

    if st.session_state.valentine_answer:
        st.markdown("---")
        st.markdown("### Valentine Certificate 🏆")
        st.balloons()


        today = datetime.now().strftime("%d %b %Y")

        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <div style="font-size:34px; margin-bottom:6px;">💗💗💗</div>
              <h2 style="margin:0; font-size:26px;">Official Valentine Certificate</h2>
              <p class="muted" style="margin:6px 0 14px 0;">Issued on {today}</p>

              <div style="font-size:16px; line-height:1.6;">
                This certifies that <b>Ren</b> has officially accepted to be my Valentine.<br>
                Decision: <b>{st.session_state.valentine_answer}</b> ✅
                <br><br>
                Valid for: unlimited forehead kisses, unlimited flirting,<br>
                and a lifetime of “come here, bebi” privileges.
              </div>

              <div style="margin-top:16px; font-size:18px;">
                Signed with love,<br>
                <b>Aanya</b> 
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='text-align:center; opacity:0.8;'>❤️ 🤍 💗 ❤️ 🤍 💗</div>",
            unsafe_allow_html=True
        )

# Footer
st.caption("Made with all my love")
