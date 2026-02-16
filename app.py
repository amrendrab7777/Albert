import streamlit as st
import groq
from duckduckgo_search import DDGS

# --- 1. PAGE CONFIG (Mobile Friendly) ---
st.set_page_config(page_title="Universal AI", page_icon="🌐", layout="centered")

# Custom CSS for a clean mobile look
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .stChatMessage { font-size: 16px !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE API LOADING ---
# This looks for the secret key you will save in Streamlit Cloud
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = groq.Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ Developer Action Required: Add 'GROQ_API_KEY' to Streamlit Cloud Secrets.")
    st.stop()

# --- 3. WEB SEARCH UTILITY ---
def get_web_info(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except:
        return "No real-time data found."

# --- 4. CHAT INTERFACE ---
st.title("🌐 Universal Intelligence")
st.caption("Connected to Llama 3 & Live Web Search")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Real-time search step
        with st.status("🔍 Searching the web...", expanded=False):
            web_context = get_web_info(prompt)
        
        # Build prompt using your RAG logic from my_rag_ai.py
        full_prompt = f"WEB CONTEXT:\n{web_context}\n\nUSER QUESTION: {prompt}"
        
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream from Groq (Professional/Fast)
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_prompt}],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})