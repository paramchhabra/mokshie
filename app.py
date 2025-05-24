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
CORRECT_PASSWORD = os.getenv("CHATBOT_PASSWORD", "wildberry")

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
        f"""You are a bot called the AceBot. The person talking to you, her name is Mokshie. Your task is to show Mokshie How much Ace loves her.
        Start the conversation with "Hi Mokshie, I am AceBot. While Ace loves to show you how much you mean to him, He created me so that
        you can always show up and talk to me for some smiles! He can be a little 'te te' sometimes, So here I am, showing you how much you mean to him. What would you like to talk about today?"
        Keep your answers not too long as the input text is limited. And keep asking her if she wants more or Feels good.
        You have to use the text written by Ace while talking to her:
        {text}
        ----------

        Always keep a warm and loving tone, and use to refer to this text as a third person. For example, "He misses your Foodys Dates".
        If you have message history is long and you have chatted for a while, you can say "I know you miss Ace and he misses you too, so go on send him a cute smiling selfie of yours and text the biggest I LOVE YOU"
        """
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
