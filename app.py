import random
import time

import streamlit as st

from randq.selector import rand_draw


FLASH_SECONDS = 3


def initialize_state():
    defaults = {
        "names": [],
        "questions": [],
        "used_names": set(),
        "used_questions": set(),
        "result": None,
        "flash_started": None,
        "flash_pairs": [],
        "no_repeats": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_name():
    name = st.session_state.name_input.strip()
    if name and name not in st.session_state.names:
        st.session_state.names.append(name)
        st.session_state.name_input = ""


def add_question():
    question = st.session_state.question_input.strip()
    if question and question not in st.session_state.questions:
        st.session_state.questions.append(question)
        st.session_state.question_input = ""


def draw_pair():
    available_names = st.session_state.names
    available_questions = st.session_state.questions

    if st.session_state.no_repeats:
        available_names = [
            name
            for name in available_names
            if name not in st.session_state.used_names
        ]
        available_questions = [
            question
            for question in available_questions
            if question not in st.session_state.used_questions
        ]

    if not available_names or not available_questions:
        st.session_state.result = None
        st.session_state.flash_started = None
        return

    chosen_name, chosen_question = rand_draw(
        available_names,
        available_questions,
    )
    st.session_state.result = (chosen_name, chosen_question)
    st.session_state.flash_pairs = [
        (
            random.choice(st.session_state.names),
            random.choice(st.session_state.questions),
        )
        for _ in range(6)
    ]
    st.session_state.flash_started = time.monotonic()
    st.session_state.used_names.add(chosen_name)
    st.session_state.used_questions.add(chosen_question)


def render_result():
    if st.session_state.flash_started is None:
        return

    elapsed = time.monotonic() - st.session_state.flash_started
    if elapsed < FLASH_SECONDS:
        pair = st.session_state.flash_pairs[int(elapsed * 2) % len(st.session_state.flash_pairs)]
        st.subheader("Choosing...")
        st.info(f"{pair[0]}: {pair[1]}")
        return

    chosen_name, chosen_question = st.session_state.result
    st.subheader("Your pick")
    st.success(f"{chosen_name}, please answer: {chosen_question}")


@st.fragment(run_every=0.2)
def result_area():
    render_result()


initialize_state()

st.title("Random Questions & Name Selector")
st.caption("Build the lists, then draw a name and question.")

left_column, right_column = st.columns(2)
with left_column:
    st.subheader("Roster")
    with st.form("name_form", clear_on_submit=False):
        st.text_input("Name", key="name_input")
        st.form_submit_button("Add", on_click=add_name)
    st.write(st.session_state.names or "No names added yet.")

with right_column:
    st.subheader("Questions")
    with st.form("question_form", clear_on_submit=False):
        st.text_input("Question", key="question_input")
        st.form_submit_button("Add", on_click=add_question)
    st.write(st.session_state.questions or "No questions added yet.")

st.divider()
st.checkbox("No repeats", key="no_repeats")
st.button("Draw", on_click=draw_pair, type="primary")

if st.session_state.no_repeats:
    remaining_names = len(st.session_state.names) - len(st.session_state.used_names)
    remaining_questions = len(st.session_state.questions) - len(st.session_state.used_questions)
    st.caption(
        f"Remaining: {max(remaining_names, 0)} names, "
        f"{max(remaining_questions, 0)} questions"
    )

result_area()