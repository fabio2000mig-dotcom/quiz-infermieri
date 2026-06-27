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

.correct {
    color: green;
    font-weight: bold;
}

.wrong {
    color: red;
    font-weight: bold;
}
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
        "options_map": {},
        "study_mode": "",
        "current_question": 0,
        "checked": False
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# =====================
# RESET
# =====================
def reset():
    st.session_state.started = False
    st.session_state.finished = False
    st.session_state.questions = []
    st.session_state.answers = {}
    st.session_state.options_map = {}
    st.session_state.study_mode = ""
    st.session_state.current_question = 0
    st.session_state.checked = False

# =====================
# START SCREEN
# =====================
if not st.session_state.started:

    col1, col2 = st.columns([1, 5])

    with col1:
        st.image("psf.png", width=150)

    with col2:
        st.markdown("<h1 style='margin-bottom:0;'>Postofissatore</h1>", unsafe_allow_html=True)
        st.markdown("<p style='margin-top:0;'>Il posto fisso è sacro!</p>", unsafe_allow_html=True)

    mode = st.radio("Modalità", ["libera", "tempo", "studio"])

    study_mode = ""

    if mode == "studio":
        study_mode = st.radio(
            "Tipo modalità studio",
            ["Modalità Studio - Lettura", "Modalità Studio - Quiz"]
        )

    if mode in ["libera", "tempo"]:
        minutes = st.number_input("Durata (minuti)", 1, 180, 10)
        num = st.number_input("Numero domande", 1, len(df), 30)
    else:
        minutes = 0
        num = len(df)

    if st.button("Avvia"):

        st.session_state.started = True
        st.session_state.finished = False
        st.session_state.current_question = 0
        st.session_state.checked = False

        if mode == "studio":
            questions = df.to_dict("records")
        else:
            questions = df.sample(num).to_dict("records")

        st.session_state.questions = questions

        options_map = {}

        for i, q in enumerate(questions):

            opts = [
                q["Risposta A"],
                q["Risposta B"],
                q["Risposta C"]
            ]

            if not (mode == "studio" and study_mode == "Modalità Studio - Lettura"):
                random.shuffle(opts)

            options_map[i] = opts

        st.session_state.options_map = options_map
        st.session_state.answers = {}
        st.session_state.mode = mode
        st.session_state.study_mode = study_mode
        st.session_state.limit = minutes * 60 if mode == "tempo" else None
        st.session_state.start_time = time.time()
        st.session_state.num = num

    st.stop()

# =====================
# MODALITA' STUDIO
# =====================
if st.session_state.mode == "studio":

    st.title("📚 Modalità Studio")

    totale = len(st.session_state.questions)

    ricerca = st.number_input(
        "Vai alla domanda numero",
        1,
        totale,
        st.session_state.current_question + 1
    )

    if ricerca != st.session_state.current_question + 1:
        st.session_state.current_question = ricerca - 1
        st.session_state.checked = False

    idx = st.session_state.current_question
    q = st.session_state.questions[idx]

    # =====================
    # NAVIGAZIONE TOP (KEY FIX)
    # =====================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Precedente", key="prev_top"):
            if st.session_state.current_question > 0:
                st.session_state.current_question -= 1
                st.session_state.checked = False
                st.rerun()

    with col2:
        if st.button("➡️ Successiva", key="next_top"):
            if st.session_state.current_question < totale - 1:
                st.session_state.current_question += 1
                st.session_state.checked = False
                st.rerun()

    st.markdown("---")

    st.markdown(f"### Domanda {idx+1} di {totale}")

    st.markdown(
        f'<div class="card">'
        f'<div class="question">{idx+1}) {q["Domanda"]}</div>',
        unsafe_allow_html=True
    )

    if st.session_state.study_mode == "Modalità Studio - Lettura":

        for opt in [q["Risposta A"], q["Risposta B"], q["Risposta C"]]:
            if opt == q["Risposta A"]:
                st.markdown(f"**✔️ {opt}**")
            else:
                st.write(opt)

    else:

        options = st.session_state.options_map[idx]

        choice = st.radio(
            "Seleziona risposta",
            options,
            key=f"studio_{idx}",
            index=None
        )

        if st.button("✅ Invio", key=f"send_{idx}"):

            if choice is not None:
                st.session_state.answers[idx] = choice

            st.session_state.checked = True

        if st.session_state.checked:

            user = st.session_state.answers.get(idx)
            correct = q["Risposta A"]

            st.markdown("---")

            for opt in options:
                if opt == correct:
                    st.markdown(f"<span class='correct'>✔️ {opt}</span>", unsafe_allow_html=True)
                elif opt == user:
                    st.markdown(f"<span class='wrong'>❌ {opt}</span>", unsafe_allow_html=True)
                else:
                    st.write(opt)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # =====================
    # NAVIGAZIONE BOTTOM (KEY FIX)
    # =====================
    col3, col4 = st.columns(2)

    with col3:
        if st.button("⬅️ Precedente", key="prev_bottom"):
            if st.session_state.current_question > 0:
                st.session_state.current_question -= 1
                st.session_state.checked = False
                st.rerun()

    with col4:
        if st.button("➡️ Successiva", key="next_bottom"):
            if st.session_state.current_question < totale - 1:
                st.session_state.current_question += 1
                st.session_state.checked = False
                st.rerun()

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

        st.markdown(f'<div class="question">{i+1}) {q["Domanda"]}</div>', unsafe_allow_html=True)

        options = st.session_state.options_map[i]

        choice = st.radio("", options, key=f"q_{i}", index=None)

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
    if st.session_state.answers.get(i) == q["Risposta A"]:
        score += 1

if score < 23:
    img = "poco.png"
    msg = "Parliamone! Anche un part time va bene!"
elif score <= 26:
    img = "medio.png"
    msg = "Meh, Meh"
else:
    img = "tanto.png"
    msg = "Come mi rilassa!"

col1, col2 = st.columns([2, 1])

with col1:
    st.success(f"Punteggio: {score}/{st.session_state.num}")
    st.markdown(f"**{msg}**")

with col2:
    st.image(img, width=120)

st.subheader("📋 Dettaglio risposte")

for i, q in enumerate(st.session_state.questions):

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="question">{i+1}) {q["Domanda"]}</div>', unsafe_allow_html=True)

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

st.markdown("---")
st.success(f"Punteggio finale: {score}/{st.session_state.num}")
st.image(img, width=150)

if st.button("🔄 Nuova prova"):
    reset()
    st.rerun()
