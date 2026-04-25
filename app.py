import streamlit as st
import pandas as pd
import random
import time

FILE = "quiz_infermieri.xlsx"
NUM_DOMANDE = 30

st.set_page_config(page_title="Quiz Infermieri", layout="wide")

# =====================
# CARICAMENTO DATI
# =====================
@st.cache_data
def load_data():
    return pd.read_excel(FILE)

df = load_data()

# =====================
# STATO SESSIONE
# =====================
if "started" not in st.session_state:
    st.session_state.started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

# =====================
# SCHERMATA INIZIALE
# =====================
if not st.session_state.started:
    st.title("🧠 Quiz Infermieri")

    mode = st.radio("Modalità", ["Libera", "A tempo"])

    minutes = 10
    if mode == "A tempo":
        minutes = st.number_input("Durata (minuti)", 1, 120, 10)

    if st.button("Avvia"):
        st.session_state.started = True
        st.session_state.questions = df.sample(NUM_DOMANDE).to_dict("records")
        st.session_state.answers = {}
        st.session_state.start_time = time.time()
        st.session_state.limit = minutes * 60

    st.stop()

# =====================
# TIMER
# =====================
if "limit" in st.session_state:
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.limit - elapsed)

    if remaining <= 0:
        st.warning("Tempo scaduto!")
        st.session_state.finished = True
    else:
        st.info(f"⏳ Tempo rimasto: {remaining//60}:{remaining%60:02}")

# =====================
# QUIZ
# =====================
st.title("Quiz")

progress = len(st.session_state.answers) / NUM_DOMANDE
st.progress(progress)

for i, q in enumerate(st.session_state.questions):
    st.markdown(f"### {i+1}) {q['Domanda']}")

    options = [
        ("A", q["Risposta A"]),
        ("B", q["Risposta B"]),
        ("C", q["Risposta C"]),
    ]

    random.shuffle(options)

    choice = st.radio(
        "Seleziona risposta",
        [text for _, text in options],
        key=f"q_{i}"
    )

    st.session_state.answers[i] = choice

# =====================
# FINE QUIZ
# =====================
if st.button("Concludi"):
    score = 0

    st.title("Risultato")

    for i, q in enumerate(st.session_state.questions):
        correct = q["Risposta A"]
        user = st.session_state.answers.get(i)

        if user == correct:
            score += 1

    st.success(f"Punteggio: {score}/{NUM_DOMANDE}")