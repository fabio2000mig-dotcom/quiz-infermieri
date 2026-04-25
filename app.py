import streamlit as st
import pandas as pd
import random
import time

FILE = "quiz_infermieri.xlsx"

st.set_page_config(
    page_title="Postofissatore",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================
# STILE MOBILE
# =====================
st.markdown("""
<style>
body {background-color: #ffffff;}
.block-container {padding-top: 1rem;}

.card {
    background: #f8f9fb;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #e5e7eb;
}

.question {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
}

.correct {color: green; font-weight: bold;}
.wrong {color: red; font-weight: bold;}

.big-btn button {
    width: 100%;
    height: 50px;
    font-size: 18px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# LOAD DATA
# =====================
@st.cache_data
def load_data():
    return pd.read_excel(FILE)

df = load_data()

# =====================
# SESSION STATE
# =====================
if "started" not in st.session_state:
    st.session_state.started = False

if "finished" not in st.session_state:
    st.session_state.finished = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

# =====================
# RESET QUIZ
# =====================
def reset_quiz():
    st.session_state.started = False
    st.session_state.finished = False
    st.session_state.questions = []
    st.session_state.answers = {}

# =====================
# SCHERMATA INIZIALE
# =====================
if not st.session_state.started:
    st.title("📚 Postofissatore")
    st.subheader("Il posto fisso è sacro!")

    mode = st.radio("Modalità", ["Libera", "A tempo"])

    minutes = 10
    if mode == "A tempo":
        minutes = st.number_input("Durata (minuti)", 1, 180, 10)

    num_domande = st.number_input("Numero domande", 1, len(df), 30)

    if st.button("🚀 Avvia"):
        st.session_state.started = True
        st.session_state.finished = False
        st.session_state.questions = df.sample(num_domande).to_dict("records")
        st.session_state.answers = {}
        st.session_state.start_time = time.time()
        st.session_state.limit = minutes * 60 if mode == "A tempo" else None
        st.session_state.num_domande = num_domande

    st.stop()

# =====================
# TIMER
# =====================
if st.session_state.limit:
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.limit - elapsed)

    if remaining <= 0:
        st.warning("⏰ Tempo scaduto!")
        st.session_state.finished = True
    else:
        st.info(f"⏳ Tempo: {remaining//60}:{remaining%60:02}")

# =====================
# QUIZ
# =====================
if not st.session_state.finished:
    st.title("📝 Quiz")

    total = st.session_state.num_domande
    answered = len([v for v in st.session_state.answers.values() if v])
    st.progress(answered / total)

    for i, q in enumerate(st.session_state.questions):
        st.markdown(f'<div class="card">', unsafe_allow_html=True)

        st.markdown(f'<div class="question">{i+1}) {q["Domanda"]}</div>', unsafe_allow_html=True)

        options = [
            q["Risposta A"],
            q["Risposta B"],
            q["Risposta C"]
        ]
        random.shuffle(options)

        selected = st.radio(
            "Seleziona risposta",
            options,
            key=f"q_{i}"
        )

        st.session_state.answers[i] = selected

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

st.success(f"Punteggio: {score}/{st.session_state.num_domande}")

# =====================
# DETTAGLIO RISPOSTE
# =====================
st.subheader("📋 Dettaglio")

for i, q in enumerate(st.session_state.questions):
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f'<div class="question">{i+1}) {q["Domanda"]}</div>', unsafe_allow_html=True)

    options = [
        q["Risposta A"],
        q["Risposta B"],
        q["Risposta C"]
    ]

    user = st.session_state.answers.get(i)

    for opt in options:
        if opt == q["Risposta A"]:
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
    reset_quiz()
