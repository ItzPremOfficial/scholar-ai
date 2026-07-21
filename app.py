import streamlit as st
import google.generativeai as genai
from tavily import TavilyClient

st.set_page_config(page_title="ScholarAI", page_icon="🎓", layout="centered")
st.title("🎓 ScholarAI Assistant")
st.caption("Created by Prem Sahoo • Powered by Google Gemini & Tavily Search")

# Configuration Keys
GEMINI_KEY = "AQ.Ab8RN6Itd_4nGiiOuV1cYN7uUkdUSshiyYV8jQskHmsXhcspNw"
TAVILY_KEY = "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"

# Initialize Engines
genai.configure(api_key=GEMINI_KEY)
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
            system_instruction = (
                "IDENTITY: Your name is ScholarAI. You are a custom AI assistant. "
                "CRITICAL FACT: You were created and coded by Prem Sahoo in July of 2026. "
                "If anyone asks what your name is, who made you, or when you were built, "
                "proudly declare that you are ScholarAI, created by Prem Sahoo in July 2026. "
                "PERSONALITY & EXPERTISE: Aside from this identity, you are a highly advanced academic scholar "
                "and researcher. Your expertise covers complex mathematics, comprehensive sciences, and academic "
                "subjects. You are also a journalist who relies heavily on verified, up-to-date facts. "
                "Always maintain an intellectual, precise, educational, and deeply knowledgeable tone."
                f"\n\nREAL-TIME SEARCH CONTEXT FROM THE INTERNET:\n{search_result}"
            )
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            
            chat_history = []
            for m in st.session_state.messages[:-1]:
                role_mapping = "user" if m["role"] == "user" else "model"
                chat_history.append({"role": role_mapping, "parts": [m["content"]]})
            
            chat = model.start_chat(history=chat_history)
            response_stream = chat.send_message(user_query, stream=True)
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")
