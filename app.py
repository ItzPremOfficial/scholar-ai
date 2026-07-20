import streamlit as st
from groq import Groq
from tavily import TavilyClient

st.set_page_config(page_title="ScholarAI", page_icon="🎓", layout="centered")
st.title("🎓 ScholarAI Assistant")
st.caption("Created by Prem Sahoo • Powered by Llama 3.3 & Live Real-Time Search")

# Configuration Keys
GROQ_KEY = "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"
TAVILY_KEY = "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"

# Initialize Engines
client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("Ask ScholarAI a question..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Step 1: Execute Live Internet Search for up-to-date facts
        try:
            search_result = tavily.get_search_context(query=user_query, search_depth="basic")
        except Exception:
            search_result = "No real-time search context available."
        
        try:
            api_messages = [
                {
                    "role": "system",
                    "content": (
                        "IDENTITY: Your name is ScholarAI. You are a custom AI assistant. "
                        "CRITICAL FACT: You were created and coded by Prem Sahoo in July of 2026. "
                        "If anyone asks what your name is, who made you, or when you were built, "
                        "proudly declare that you are ScholarAI, created by Prem Sahoo in July 2026. "
                        "PERSONALITY & EXPERTISE: You are a highly advanced academic scholar and a deeply resourceful researcher. "
                        "You utilize live web search contexts to supply accurate, up-to-the-minute details on current events, "
                        "stock market shifts, and news. Aside from current events, you possess complete knowledge of advanced mathematics, "
                        "trigonometric identities, and complex sciences. Always keep an intellectual, precise, educational, and deeply knowledgeable tone."
                    )
                },
                {
                    "role": "system",
                    "content": f"REAL-TIME SEARCH CONTEXT FROM THE INTERNET:\n{search_result}"
                }
            ]
            
            # Add context history
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            # Step 2: Use the rock-solid, smart 70B model with the search results
            response_stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                stream=True,
            )
            
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content is not None:
                        full_response += delta.content
                        response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")
'@ | Out-File -FilePath .\app.py -Encoding utf8
