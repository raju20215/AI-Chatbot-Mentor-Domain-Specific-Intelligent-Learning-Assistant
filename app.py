import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# ------------------ SETUP ------------------
st.set_page_config(
    page_title="AI Chatbot Mentor",
    page_icon="🤖",
    layout="centered"
)

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("gemini")
)

# ------------------ SESSION STATE ------------------
if "selected_module" not in st.session_state:
    st.session_state.selected_module = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ MODULES ------------------
MODULES = {
    "Python": "Python programming, syntax, libraries, data structures, OOP",
    "SQL": "SQL queries, joins, databases, optimization",
    "Power BI": "Dashboards, DAX, data visualization",
    "EDA": "Exploratory Data Analysis, statistics, visualization",
    "Machine Learning": "ML algorithms, training, evaluation",
    "Deep Learning": "Neural networks, CNNs, RNNs",
    "Generative AI": "LLMs, prompt engineering, GenAI apps",
    "Agentic AI": "AI agents, autonomous systems, LangChain"
}

# ------------------ MODULE SELECTION ------------------
if st.session_state.selected_module is None:
    st.title("👋 Welcome to AI Chatbot Mentor")
    st.write("Select a learning module to begin.")

    selected = st.selectbox("Choose a module:", MODULES.keys())

    if st.button("Start Learning", type="primary"):
        st.session_state.selected_module = selected
        st.session_state.messages = []
        st.rerun()

# ------------------ CHAT INTERFACE ------------------
else:
    module = st.session_state.selected_module

    st.title(f"{module} AI Mentor 🎯")
    st.write(f"I help only with **{module}** questions.")

    st.divider()

    # Display chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask your question...")

    if user_input:
        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        # System prompt
        system_prompt = f"""
You are an AI mentor specialized ONLY in {module}.

Rules:
1. Answer ONLY questions related to {MODULES[module]}
2. If unrelated, reply EXACTLY:
   "Sorry, I don't know about this question. Please ask something related to {module}."
3. Be clear and educational.
"""

        # Build prompt with memory
        prompt = system_prompt

        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"\n{role}: {msg['content']}"

        prompt += "\n\nAssistant:"

        # Call model
        response = model.invoke(prompt)

        ai_response = (
            response.content[0]["text"]
            if isinstance(response.content, list)
            else response.content
        )
        print(prompt)
        # Save AI response
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response
        })
        print(st.session_state.messages)
        with st.chat_message("assistant"):
            st.write(ai_response)

    # ------------------ FOOTER ACTIONS ------------------
    if st.session_state.messages:
        st.divider()
        col1, col2 = st.columns([3, 1])

        with col1:
            chat_text = f"{module} AI Mentor Session\n" + "=" * 50 + "\n\n"
            for msg in st.session_state.messages:
                role = "You" if msg["role"] == "user" else "AI"
                chat_text += f"{role}: {msg['content']}\n\n"

            st.download_button(
                "📥 Download Conversation",
                chat_text,
                file_name=f"{module}_chat.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            if st.button("🔄 Change Module", use_container_width=True):
                st.session_state.selected_module = None
                st.session_state.messages = []
                st.rerun()
