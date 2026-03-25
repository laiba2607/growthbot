import streamlit as st
from groq import Groq
import os
import time

# ==========================================
# SECURE API KEY HANDLING
# ==========================================
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    api_key = os.environ.get("GROQ_API_KEY")

# ==========================================
# CORE LOGIC
# ==========================================
class AIGrowthBot:
    def __init__(self, key):
        self.client = Groq(api_key=key)

        self.system_instruction = {
            "role": "system",
            "content": "You are GrowthBot, an encouraging chatbot focused on personal growth, learning, and improving fundamentals. Keep answers clear, concise, and friendly."
        }

    def generate_response(self, memory_log):
        try:
            messages = [self.system_instruction] + memory_log

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content or "Sorry, I couldn't respond properly."

        except Exception as e:
            return f"Oops! Error: {e}"

# ==========================================
# UI SETUP
# ==========================================
st.set_page_config(page_title="GrowthBot", page_icon="🌱")

st.title("🌱 AI GrowthBot")
def get_greeting():
    return f"Hello {st.session_state.user_name or 'there'}! I am GrowthBot 🌱 Let's grow together!"

# ==========================================
# THEME TOGGLE
# ==========================================
# =========================
# THEME TOGGLE (FIXED)
# =========================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

toggle = st.toggle(
    "🌙 Dark Mode",
    value=(st.session_state.theme == "dark")
)

if toggle:
    st.session_state.theme = "dark"
else:
    st.session_state.theme = "light"
    st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }

    /* ALL TEXT */
    .stApp, .stMarkdown, p, span, div {
        color: black !important;
    }

    /* FIX CHAT INPUT (IMPORTANT) */
    div[data-testid="stChatInput"] textarea {
        background-color: #f1f5f9 !important;
        color: black !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }

    /* NORMAL INPUT */
    input {
        background-color: white !important;
        color: black !important;
    }

    /* BUTTON */
    button {
        background-color: #e2e8f0 !important;
        color: black !important;
    }

    </style>
""", unsafe_allow_html=True)

# ==========================================
# USER NAME MEMORY
# ==========================================
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

name = st.text_input("Enter your name:", value=st.session_state.user_name)

if name:
    st.session_state.user_name = name

    # Update greeting if exists
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        if "Hello" in st.session_state.messages[0]["content"]:
            st.session_state.messages[0]["content"] = get_greeting()

# ==========================================
# CLEAR CHAT BUTTON
# ==========================================
if st.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Chat cleared! {get_greeting()}"
    })

# ==========================================
# MAIN APP
# ==========================================
if not api_key:
    st.error("GROQ_API_KEY missing!")
    st.stop()

bot = AIGrowthBot(api_key)

# Initialize memory
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
       "content": get_greeting()
    })

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# CHAT INPUT
# ==========================================
if user_prompt := st.chat_input("Type your message..."):

    # Show user msg
    with st.chat_message("user"):
        st.markdown(user_prompt)

    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Generate response
    with st.spinner("Thinking..."):
        response = bot.generate_response(st.session_state.messages)

    # Typing animation
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        for word in response.split():
            full_response += word + " "
            placeholder.markdown(full_response + "▌")
            time.sleep(0.03)

        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})