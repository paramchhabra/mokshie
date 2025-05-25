import streamlit as st
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from dotenv import load_dotenv
import os
import time
import json
from langchain.callbacks.tracers.langchain import LangChainTracer


load_dotenv()

# ----- PASSWORD SETUP -----
CORRECT_PASSWORD = os.getenv("CHATBOT_PASSWORD")

# ----- AUTHENTICATION -----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒Prove That you are My Mokshie😤")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.success("Welcome Babyyyyyyyy <3")
            time.sleep(2)
            st.rerun()
        else:
            st.error("😤ure not mokshie get out.")
    st.stop()


text = os.getenv("TEXT")
# ----- SYSTEM PROMPT -----
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = os.getenv(
        "SYSTEM_PROMPT",
        text
    )

# ----- CSS STYLING -----
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        background-color: #53c3ff !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
        background-color: #53c3ff !important;
    }
    [data-testid="stChatInput"], [data-testid="chat-input-container"],
    div[class*="stChatInputContainer"], section[tabindex="0"] > div:nth-child(2),
    section[tabindex="0"] > div:nth-child(2) > div {
        background-color: #53c3ff !important;
    }
    .appview-container > div:last-child {
        background-color: #53c3ff !important;
    }
    div:has(textarea) {
        background-color: #53c3ff !important;
    }
    textarea, input {
        background-color: #fff0f5 !important;
        color: black !important;
        border-top-left-radius: 20px !important;
        border-bottom-left-radius: 20px !important;
        border-top-right-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }
    button[kind="primary"] {
        background-color: #ff66b2 !important;
        border: none !important;
    }
    footer, [class*="css"] {
        background-color: #53c3ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----- INITIALIZE LLM AND MEMORY -----
if "groq_llm" not in st.session_state:
    st.session_state.groq_llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

# ----- PROMPT TEMPLATE -----
chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(st.session_state.system_prompt),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# ----- CONVERSATION CHAIN -----
if "conversation" not in st.session_state:
    tracer = LangChainTracer()
    st.session_state.conversation = ConversationChain(
        llm=st.session_state.groq_llm,
        memory=st.session_state.memory,
        prompt=chat_prompt,
        callbacks=[tracer],
        verbose=False
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----- BOT FIRST MESSAGE -----
if len(st.session_state.chat_history) == 0:
    # Let the bot say something first with empty input or a trigger phrase
    initial_bot_msg = st.session_state.conversation.predict(input="")
    st.session_state.chat_history.append(("Bot", initial_bot_msg))

# ----- CHAT UI -----
st.title("❤️ To Mokshie, From Ace")

user_input = st.chat_input("Type your message here...")

if user_input:
    response = st.session_state.conversation.predict(input=user_input)
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", response))

# Display chat messages
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)
