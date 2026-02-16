import streamlit as st
import groq
from duckduckgo_search import DDGS

# 1. Page Config for Mobile/Tablet Responsiveness
st.set_page_config(page_title="AI Agent", layout="centered", page_icon="🤖")

# Professional Styling
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    /* Mobile-friendly input */
    .stChatInput { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Web Search Logic (Same as your my_rag_ai.py)
def get_web_context(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except:
        return ""

# 3. Sidebar for API Key (Necessary for public use)
with st.sidebar:
    st.title("Settings")
    user_api_key = st.text_input("Groq API Key", type="password")
    st.write("Get a free key at [console.groq.com](https://console.groq.com)")

# 4. Chat Interface
st.title("🌐 Universal AI")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    if not user_api_key:
        st.error("Please add your Groq API Key in the sidebar!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Real-time search
        context = get_web_context(prompt)
        
        # Connect to Groq Cloud (Professional grade)
        client = groq.Groq(api_key=user_api_key)
        
        # Build prompt using your RAG logic
        full_prompt = f"Using this info: {context}\n\nQuestion: {prompt}"
        
        response_placeholder = st.empty()
        full_response = ""
        
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_prompt}],
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})