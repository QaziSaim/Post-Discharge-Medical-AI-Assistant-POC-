import streamlit as st
from patient_lookup import load_patient_data, find_patient_by_name
from clinical_agent import run_clinical_agent
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename="full_medai_session.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

patient_data = load_patient_data("patient_reports.json")

st.set_page_config(page_title="MedAI Assistant", page_icon="🩺")
st.title("🩺 Post-Discharge Medical AI Assistant")

st.markdown("""
### 👋 Welcome to MedAI Assistant!
Please begin by typing your **full name** as it appears on your discharge report.
""")

if "state" not in st.session_state:
    st.session_state.state = "awaiting_name"
    st.session_state.name = ""
    st.session_state.report = None
    st.session_state.q_index = 0
    st.session_state.chat = []
    st.session_state.questions = []
    st.session_state.answered = []
    st.session_state.in_clinical_mode = False
    st.session_state.followup_mode = False
    st.session_state.exit_ready = False

def get_questions(report):
    return [
        f"Are you taking your medications as prescribed: {', '.join(report['medications'])}?",
        f"Are you following your dietary restrictions: {', '.join(report['dietary_restrictions']) if isinstance(report['dietary_restrictions'], list) else report['dietary_restrictions']}?",
        f"Have you noticed any warning signs like {', '.join(report['warning_signs']) if isinstance(report['warning_signs'], list) else report['warning_signs']}?",
        f"Have you scheduled your follow-up: {', '.join(report['follow_up']) if isinstance(report['follow_up'], list) else report['follow_up']}?"
    ]

def is_medical_query(text):
    keywords = ["pain", "swelling", "urine", "blood", "symptom", "dizzy", "nausea", "vomiting", "gfr", "kidney", "ai", "2025", "ml", "machine learning", "chatgpt", "dialysis", "drug", "nephrology"]
    return any(k in text.lower() for k in keywords)

for role, msg in st.session_state.chat:
    if role == "receptionist":
        with st.chat_message("assistant", avatar="🧑‍💼"):
            st.markdown(f"**Receptionist Agent:**\n\n{msg}")
    elif role == "clinical":
        with st.chat_message("assistant", avatar="🧑‍⚕️"):
            st.markdown(f"**Clinical Agent:**\n\n{msg}")
    elif role == "source":
        with st.chat_message("assistant"):
            st.markdown(f"*{msg}*")
    elif role == "user":
        with st.chat_message("user"):
            st.markdown(msg)

user_input = st.chat_input("Type your response here...")

if user_input:
    st.session_state.chat.append(("user", user_input))
    logging.info(f"User ({st.session_state.name}): {user_input}")
    with st.chat_message("user"):
        st.markdown(user_input)

    if st.session_state.state == "awaiting_name":
        result = find_patient_by_name(user_input, patient_data)
        if isinstance(result, str):
            bot_msg = result
        elif isinstance(result, list):
            bot_msg = "Multiple matches found. Please enter full name with more detail."
        else:
            st.session_state.name = result["patient_name"]
            st.session_state.report = result
            st.session_state.questions = get_questions(result)
            st.session_state.state = "asking_questions"
            question = st.session_state.questions[st.session_state.q_index]
            bot_msg = f"Hello **{result['patient_name']}**! Your diagnosis is **{result['primary_diagnosis']}**.\n\n{question}"

        st.session_state.chat.append(("receptionist", bot_msg))
        logging.info(f"Receptionist: {bot_msg}")
        with st.chat_message("receptionist"):
            st.markdown(bot_msg)

    elif st.session_state.state == "asking_questions":
        if is_medical_query(user_input):
            st.session_state.in_clinical_mode = True
            st.session_state.state = "clinical_mode"
            st.session_state.chat.append(("receptionist", "Forwarding to Clinical Agent for medical assistance..."))
            logging.info("Receptionist: Forwarding to Clinical Agent for medical assistance...")
            with st.chat_message("receptionist"):
                st.markdown("Forwarding to Clinical Agent for medical assistance...")

            with st.spinner("Clinical Agent is analyzing..."):
                response, src = run_clinical_agent(user_input)

            st.session_state.chat.append(("clinical", response))
            logging.info(f"Clinical Agent: {response}")
            with st.chat_message("clinical"):
                st.markdown(response)

            st.session_state.chat.append(("source", src))
            logging.info(f"Source: {src}")
            with st.chat_message("source"):
                st.markdown(f"**{src}**")

        else:
            if st.session_state.q_index not in st.session_state.answered:
                st.session_state.answered.append(st.session_state.q_index)
            st.session_state.q_index += 1
            if st.session_state.q_index < len(st.session_state.questions):
                next_q = st.session_state.questions[st.session_state.q_index]
                st.session_state.chat.append(("receptionist", next_q))
                logging.info(f"Receptionist: {next_q}")
                with st.chat_message("receptionist"):
                    st.markdown(next_q)
            else:
                st.session_state.state = "clinical_mode"
                closing_msg = "Thanks for your answers. Let me know any medical issues you're facing."
                st.session_state.chat.append(("receptionist", closing_msg))
                logging.info(f"Receptionist: {closing_msg}")
                with st.chat_message("receptionist"):
                    st.markdown(closing_msg)

    elif st.session_state.state == "clinical_mode":
        lower_input = user_input.strip().lower()

        if lower_input in ["bye", "exit", "thank you", "thanks"]:
            farewell = "I hope I was able to answer all your medical queries. Transferring you back to the receptionist for any final checkups."
            st.session_state.chat.append(("clinical", farewell))
            logging.info(f"Clinical Agent: {farewell}")
            with st.chat_message("clinical"):
                st.markdown(farewell)

            st.session_state.state = "followup_mode"
            st.session_state.q_index = 0

            for i in range(len(st.session_state.questions)):
                if i not in st.session_state.answered:
                    q = st.session_state.questions[i]
                    st.session_state.chat.append(("receptionist", q))
                    logging.info(f"Receptionist: {q}")
                    with st.chat_message("receptionist"):
                        st.markdown(q)
                    st.session_state.q_index = i
                    break
            else:
                st.session_state.state = "chatting"
                wrap_msg = "Is there anything else I can assist you with?"
                st.session_state.chat.append(("receptionist", wrap_msg))
                logging.info(f"Receptionist: {wrap_msg}")
                with st.chat_message("receptionist"):
                    st.markdown(wrap_msg)

        else:
            st.session_state.chat.append(("receptionist", "Forwarding to Clinical Agent for medical assistance..."))
            logging.info("Receptionist: Forwarding to Clinical Agent for medical assistance...")
            with st.chat_message("receptionist"):
                st.markdown("Forwarding to Clinical Agent for medical assistance...")

            with st.spinner("Clinical Agent is analyzing..."):
                response, src = run_clinical_agent(user_input)

            st.session_state.chat.append(("clinical", response))
            logging.info(f"Clinical Agent: {response}")
            with st.chat_message("clinical"):
                st.markdown(response)

            st.session_state.chat.append(("source", src))
            logging.info(f"Source: {src}")
            with st.chat_message("source"):
                st.markdown(f"**{src}**")

    elif st.session_state.state == "followup_mode":
        if st.session_state.q_index < len(st.session_state.questions):
            if st.session_state.q_index not in st.session_state.answered:
                st.session_state.answered.append(st.session_state.q_index)
            st.session_state.q_index += 1
            for i in range(st.session_state.q_index, len(st.session_state.questions)):
                if i not in st.session_state.answered:
                    q = st.session_state.questions[i]
                    st.session_state.chat.append(("receptionist", q))
                    logging.info(f"Receptionist: {q}")
                    with st.chat_message("receptionist"):
                        st.markdown(q)
                    st.session_state.q_index = i
                    break
            else:
                st.session_state.state = "chatting"
                st.session_state.chat.append(("receptionist", "Is there anything else I can assist you with?"))
                logging.info("Receptionist: Is there anything else I can assist you with?")
                with st.chat_message("receptionist"):
                    st.markdown("Is there anything else I can assist you with?")

    elif st.session_state.state == "chatting":
        lower_input = user_input.strip().lower()
        if lower_input in ["bye", "exit", "goodbye"]:
            farewell = "Thank you for using MedAI Assistant. Wishing you good health and a speedy recovery! 👋"
            st.session_state.chat.append(("receptionist", farewell))
            logging.info(f"Receptionist: {farewell}")
            with st.chat_message("receptionist"):
                st.markdown(farewell)
            st.session_state.state = "done"
        elif is_medical_query(user_input):
            st.session_state.state = "clinical_mode"
        else:
            if st.session_state.q_index < len(st.session_state.questions):
                if st.session_state.q_index not in st.session_state.answered:
                    st.session_state.answered.append(st.session_state.q_index)
                st.session_state.q_index += 1
                for i in range(st.session_state.q_index, len(st.session_state.questions)):
                    if i not in st.session_state.answered:
                        q = st.session_state.questions[i]
                        st.session_state.chat.append(("receptionist", q))
                        logging.info(f"Receptionist: {q}")
                        with st.chat_message("receptionist"):
                            st.markdown(q)
                        st.session_state.q_index = i
                        break
            else:
                final_msg = "You may still ask questions or type 'bye' to end the session."
                st.session_state.chat.append(("receptionist", final_msg))
                logging.info(f"Receptionist: {final_msg}")
                with st.chat_message("receptionist"):
                    st.markdown(final_msg)