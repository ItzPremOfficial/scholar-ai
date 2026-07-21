@'
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

st.set_page_config(page_title="ScholarAI", page_icon="🎓", layout="centered")
st.title("🎓 ScholarAI Assistant")
st.caption("Created by Prem Sahoo • Powered by Together AI & Tavily Search")

# Configuration Keys
TOGETHER_KEY = "333239618681214e08e8c2c830ba1a9f22bb6c28641d75a26b79a78b877dcecc"
TAVILY_KEY = "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"

# FIXED: Pointing directly to the correct v1 endpoint
client = OpenAI(api_key=TOGETHER_KEY, base_url="https://together.xyz")
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
        
        try:
            with st.spinner("Searching the web..."):
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
                        "PERSONALITY & EXPERTISE: Aside from this identity, you are a highly advanced academic scholar "
                        "and researcher. Your expertise covers complex mathematics, comprehensive sciences, and academic "
                        "subjects. You are also a journalist who relies heavily on verified, up-to-date facts. "
                        "Always maintain an intellectual, precise, educational, and deeply knowledgeable tone."
                    )
                },
                {
                    "role": "system",
                    "content": f"REAL-TIME SEARCH CONTEXT FROM THE INTERNET:\n{search_result}"
                }
            ]
            
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            response_stream = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
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
