import streamlit as st
import groq
from duckduckgo_search import DDGS

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Albert",
    page_icon="🤖",
    layout="centered", # Optimized for Mobile and Tablets
    initial_sidebar_state="collapsed"
)

# Custom Styling for a Professional Feel
st.markdown("""
    <style>
    .stApp { max-width: 850px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; font-size: 16px; }
    .stChatInput { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE API LOADING ---
# Ensure you add GROQ_API_KEY to your Streamlit Cloud Secrets
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = groq.Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ Developer Setup Required: Please add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 3. WEB SEARCH ENGINE ---
def get_web_context(query):
    """Albert's web search engine to get real-time facts."""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except Exception:
        return "Search currently unavailable. Responding with internal knowledge."

# --- 4. ALBERT CHAT INTERFACE ---
st.title("🤖 I am Albert")
st.caption("Professional AI Assistant • Live Web Search • Powered by Groq")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Albert's Response
    with st.chat_message("assistant"):
        # Real-time Web Search
        with st.status("🔍 Albert is searching the web...", expanded=False):
            context = get_web_context(prompt)
            st.write("Processing information...")

        # System Prompt for Albert
        system_instructions = (
            f"You are Albert, a professional and helpful AI assistant. "
            f"Use the following web data to provide an accurate answer: {context}\n\n"
            f"User Question: {prompt}"
        )
        
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream the response for a professional feel
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": system_instructions}],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Albert encountered an error: {str(e)}")

    # Save to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
