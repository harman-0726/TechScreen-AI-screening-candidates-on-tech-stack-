import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from prompt_templates import generate_technical_questions_prompt
import re

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

EXIT_KEYWORDS = ["exit", "quit", "bye"]

# Streamlit settings
st.set_page_config(page_title="TalentScout AI", layout="centered")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "submitted_answers" not in st.session_state:
    st.session_state.submitted_answers = False

# Clear input callback
def clear_input():
    st.session_state.chat_input = ""

# Groq call function
def ask_groq(prompt, model="llama3-70b-8192"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a polite AI hiring assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# MCQ parser
def parse_mcq_questions(raw_text):
    questions = []
    lines = raw_text.strip().split("\n")

    current = {"question": "", "options": [], "answer": ""}
    question_pattern = re.compile(r"^Q\d+\.\s*(.*)")
    option_pattern = re.compile(r"^[a-dA-D]\)\s*(.*)")
    answer_pattern = re.compile(r"^Answer\s*:\s*([a-dA-D])")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        q_match = question_pattern.match(line)
        opt_match = option_pattern.match(line)
        ans_match = answer_pattern.match(line)

        if q_match:
            if current["question"]:
                questions.append(current)
                current = {"question": "", "options": [], "answer": ""}
            current["question"] = line

        elif opt_match:
            current["options"].append(line)

        elif ans_match:
            current["answer"] = ans_match.group(1).lower()

    if current["question"]:
        questions.append(current)

    return questions

# UI
st.title("🤖 TalentScout AI")
st.markdown("Welcome to TalentScout! I'm your AI hiring assistant here to help with initial candidate screening. Type **exit** anytime to end.")

# User input
st.text_input("👤 You:", placeholder="Say something...", key="chat_input", on_change=clear_input)
user_input = st.session_state.get("chat_input", "").strip()

# Exit handler
if user_input.lower() in EXIT_KEYWORDS:
    st.session_state.chat_history.append(("👤", user_input))
    st.session_state.chat_history.append(("🤖", "Thanks for your time! We'll contact you shortly. Goodbye!"))
    for speaker, msg in st.session_state.chat_history:
        st.write(f"**{speaker}**: {msg}")
    st.stop()

# Candidate form
if not st.session_state.candidate_data:
    with st.form("candidate_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        experience = st.number_input("Years of Experience", min_value=0, step=1)
        role = st.text_input("Desired Position(s)")
        location = st.text_input("Current Location")
        tech_stack = st.text_area("Tech Stack (Languages, Frameworks, Databases, Tools)")

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state.candidate_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "experience": experience,
                "role": role,
                "location": location,
                "tech_stack": tech_stack
            }
            st.success("✅ Info submitted! Scroll down to answer your technical questions.")

# Generate technical MCQs
if st.session_state.candidate_data and not st.session_state.questions:
    tech_stack = st.session_state.candidate_data["tech_stack"]
    prompt = generate_technical_questions_prompt(tech_stack)
    questions_raw = ask_groq(prompt)
    parsed_mcqs = parse_mcq_questions(questions_raw)
    st.session_state.questions = parsed_mcqs

# MCQ answer form
if st.session_state.questions and not st.session_state.submitted_answers:
    st.subheader("🧠 Answer Technical MCQs")
    with st.form("answers_form"):
        for i, item in enumerate(st.session_state.questions):
            st.write(f"**Q{i+1}. {item['question'][3:].strip()}**")
            for opt in item['options']:
                st.write(opt)
            selected = st.radio(f"Your Answer to Q{i+1}", ['a', 'b', 'c', 'd'], key=f"answer_q{i+1}")
            st.session_state.answers[f"q{i+1}"] = selected
        submit_answers = st.form_submit_button("Submit Answers")
        if submit_answers:
            st.session_state.submitted_answers = True
            st.success("✅ Answers submitted! Evaluating...")

# Evaluation results
if st.session_state.submitted_answers:
    st.subheader("📊 Evaluation Results")
    total_score = 0
    max_score = len(st.session_state.questions) * 10
    for i, item in enumerate(st.session_state.questions):
        user_ans = st.session_state.answers.get(f"q{i+1}", "").lower()
        correct_ans = item["answer"]
        st.markdown(f"**Q{i+1}: {item['question'][3:].strip()}**")
        for opt in item["options"]:
            st.markdown(opt)
        st.markdown(f"**Your Answer:** {user_ans}")
        st.markdown(f"**Correct Answer:** {correct_ans}")
        score = 10 if user_ans == correct_ans else 0
        total_score += score
        st.markdown(f"**Score for this question: {score}/10**")
        st.markdown("---")

    st.markdown(f"### 🏁 Total Score: **{total_score} / {max_score}**")

# Fallback chat
if user_input and st.session_state.candidate_data:
    st.session_state.chat_history.append(("👤", user_input))
    fallback = "I didn't catch that. Please clarify or type 'exit' to finish."
    st.session_state.chat_history.append(("🤖", fallback))

# Display chat history
for speaker, msg in st.session_state.chat_history:
    st.write(f"**{speaker}**: {msg}")
