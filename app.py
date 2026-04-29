import streamlit as st
import pandas as pd
import random
import time

FILE = "quiz_infermieri.xlsx"

st.set_page_config(page_title="Postofissatore", layout="centered")

# =====================
# STILE (CHIARO)
# =====================
st.markdown("""
<style>
body {background-color: #ffffff;}
.card {
    background: #f8f9fb;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    border: 1px solid #e5e7eb;
}
.question {
    font-size: 18px;
    font-weight: bold;
    color: #1f2937;
}
.correct {color: green; font-weight: bold;}
.wrong {color: red; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# =====================
# DATA
# =====================
@st.cache_data
def load():
    return pd.read_excel(FILE)

df = load()

# =====================
# STATE INIT
# =====================
def init():
    defaults = {
        "started": False,
        "finished": False,
        "questions": [],
        "answers": {},
        "mode": "libera",
        "limit": None,
        "num": 30,
        "options_map": {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# =====================
# RESET
# =====================
def reset():
    for k in ["started", "finished", "questions", "answers", "options_map"]:
        if k in ["started", "finished"]:
            st.session_state[k] = False
        else:
            st.session_state[k] = {} if k != "questions" else []

# =====================
# START SCREEN
# =====================
if not st.session_state.started:
    col1, col2 = st.columns([1, 5])

    with col1:
        st.image("psf.png", width=150)

    with col2:
        st.markdown(
            "<h1 style='margin-bottom:0;'>Postofissatore</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='margin-top:0;'>Il posto fisso è sacro!</p>",
            unsafe_allow_html=True
        )

    mode = st.radio("Modalità", ["libera", "tempo"])
    minutes = st.number_input("Durata (minuti)", 1, 180, 10)
    num = st.number_input("Numero domande", 1, len(df), 30)

    if st.button("Avvia"):
        st.session_state.started = True
        st.session_state.finished = False

        questions = df.sample(num).to_dict("records")
        st.session_state.questions = questions

        options_map = {}
        for i, q in enumerate(questions):
            opts = [
                q["Risposta A"],
                q["Risposta B"],
                q["Risposta C"]
            ]
            random.shuffle(opts)
            options_map[i] = opts

        st.session_state.options_map = options_map
        st.session_state.answers = {}
        st.session_state.mode = mode
        st.session_state.limit = minutes * 60 if mode == "tempo" else None
        st.session_state.start_time = time.time()
        st.session_state.num = num

    st.stop()

# =====================
# TIMER
# =====================
if st.session_state.mode == "tempo" and not st.session_state.finished:
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.limit - elapsed)

    if remaining <= 0:
        st.warning("⏰ Tempo scaduto!")
        st.session_state.finished = True
    else:
        st.info(f"⏳ Tempo: {remaining//60:02}:{remaining%60:02}")

# =====================
# QUIZ
# =====================
if not st.session_state.finished:
    st.title("📝 Quiz")

    for i, q in enumerate(st.session_state.questions):
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(
            f'<div class="question">{i+1}) {q["Domanda"]}</div>',
            unsafe_allow_html=True
        )

        options = st.session_state.options_map[i]

        choice = st.radio(
            "",
            options,
            key=f"q_{i}",
            index=None
        )

        if choice is not None:
            st.session_state.answers[i] = choice

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✅ Concludi prova"):
        st.session_state.finished = True

    st.stop()

# =====================
# RISULTATO
# =====================
st.title("📊 Risultato")

score = 0

for i, q in enumerate(st.session_state.questions):
    user = st.session_state.answers.get(i)
    correct = q["Risposta A"]

    if user == correct:
        score += 1

# SELEZIONE IMMAGINE + TESTO
if score < 23:
    img = "poco.png"
    msg = "Parliamone! Anche un parti time va bene!"
elif 23 <= score <= 26:
    img = "medio.png"
    msg = "Meh, Meh"
else:
    img = "tanto.png"
    msg = "Come mi rilassa!"

# LAYOUT AFFIANCATO
col1, col2 = st.columns([2, 1])

with col1:
    st.success(f"Punteggio: {score}/{st.session_state.num}")
    st.markdown(f"**{msg}**")

with col2:
    st.image(img, width=120)

# =====================
# DETTAGLIO
# =====================
st.subheader("📋 Dettaglio risposte")

for i, q in enumerate(st.session_state.questions):
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        f'<div class="question">{i+1}) {q["Domanda"]}</div>',
        unsafe_allow_html=True
    )

    options = st.session_state.options_map[i]
    user = st.session_state.answers.get(i)
    correct = q["Risposta A"]

    for opt in options:
        if opt == correct:
            st.markdown(f"<span class='correct'>✔️ {opt}</span>", unsafe_allow_html=True)
        elif opt == user:
            st.markdown(f"<span class='wrong'>❌ {opt}</span>", unsafe_allow_html=True)
        else:
            st.write(opt)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================
# RISULTATO FINALE
# =====================
st.markdown("---")
st.subheader("🏁 Risultato finale")

st.success(f"Punteggio finale: {score}/{st.session_state.num}")
st.markdown(f"**{msg}**")
st.image(img, width=150)

# =====================
# RIAVVIO
# =====================
if st.button("🔄 Nuova prova"):
    reset()
