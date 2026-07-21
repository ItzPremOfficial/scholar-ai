import streamlit as st
from google import genai
from google.genai import types
from tavily import TavilyClient

st.set_page_config(page_title="ScholarAI", page_icon="🎓", layout="centered")
st.title("🎓 ScholarAI Assistant")
st.caption("Created by Prem Sahoo • Powered by Google Gemini & Tavily Search")

# Configuration Keys
GEMINI_KEY = "AQ.Ab8RN6Itd_4nGiiOuV1cYN7uUkdUSshiyYV8jQskHmsXhcspNw"
TAVILY_KEY = "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"

# Initialize Upgraded Next-Gen Engines
client = genai.Client(api_key=GEMINI_KEY)
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
            # Reconstruct the system instructions and layout for the new Client structure
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
            
            # Format chat tracking history arrays correctly for next-gen models
            formatted_contents = []
            for m in st.session_state.messages:
                # Map roles correctly to match user/model expectations
                role_val = "user" if m["role"] == "user" else "model"
                formatted_contents.append(
                    types.Content(role=role_val, parts=[types.Part.from_text(text=m["content"])])
                )
            
            # Requesting stream generation over the optimized model endpoint
            response_stream = client.models.generate_content_stream(
                model='gemini-1.5-flash',
                contents=formatted_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")
