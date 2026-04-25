import streamlit as st
import pandas as pd
import random
import time

FILE = "quiz_infermieri.xlsx"

st.set_page_config(page_title="Postofissatore", layout="centered")

# =====================
# STILE
# =====================
st.markdown("""
<style>
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
# STATE
# =====================
def init():
    for k, v in {
        "started": False,
        "finished": False,
        "questions": [],
        "answers": {},
        "mode": "libera",
        "limit": None,
        "num": 30
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

def reset():
    for k in ["started","finished","questions","answers"]:
        st.session_state[k] = False if k in ["started","finished"] else {}

# =====================
# START SCREEN
# =====================
if not st.session_state.started:
    st.title("📚 Postofissatore")
    st.subheader("Il posto fisso è sacro!")

    mode = st.radio("Modalità", ["libera", "tempo"])
    minutes = st.number_input("Durata (minuti)", 1, 180, 10)
    num = st.number_input("Numero domande", 1, len(df), 30)

    if st.button("Avvia"):
        st.session_state.started = True
        st.session_state.finished = False
        st.session_state.questions = df.sample(num).to_dict("records")
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
# QUIZ (NO LIVE UPDATE)
# =====================
if not st.session_state.finished:
    st.title("📝 Quiz")

    for i, q in enumerate(st.session_state.questions):
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(f'<div class="question">{i+1}) {q["Domanda"]}</div>', unsafe_allow_html=True)

        options = [
            q["Risposta A"],
            q["Risposta B"],
            q["Risposta C"]
        ]
        random.shuffle(options)

        choice = st.radio(
            "Seleziona risposta",
            [""] + options,  # 👈 permette stato iniziale vuoto
            key=f"q_{i}"
        )

        if choice != "":
            st.session_state.answers[i] = choice

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✅ Concludi prova"):
        st.session_state.finished = True

    st.stop()

# =====================
# RISULTATI
# =====================
st.title("📊 Risultato")

score = 0

for i, q in enumerate(st.session_state.questions):
    user = st.session_state.answers.get(i)
    correct = q["Risposta A"]

    if user == correct:
        score += 1

st.success(f"Punteggio: {score}/{st.session_state.num}")

# =====================
# DETTAGLIO RISPOSTE
# =====================
st.subheader("📋 Dettaglio risposte")

for i, q in enumerate(st.session_state.questions):
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f'<div class="question">{i+1}) {q["Domanda"]}</div>', unsafe_allow_html=True)

    user = st.session_state.answers.get(i)
    correct = q["Risposta A"]

    options = [
        q["Risposta A"],
        q["Risposta B"],
        q["Risposta C"]
    ]

    for opt in options:
        if opt == correct:
            st.markdown(f"<span class='correct'>✔️ {opt}</span>", unsafe_allow_html=True)
        elif opt == user:
            st.markdown(f"<span class='wrong'>❌ {opt}</span>", unsafe_allow_html=True)
        else:
            st.write(opt)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================
# RIAVVIO
# =====================
if st.button("🔄 Nuova prova"):
    reset()
