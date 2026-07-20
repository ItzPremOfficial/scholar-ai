import streamlit as st
from groq import Groq

st.set_page_config(page_title="ScholarAI", page_icon="🎓", layout="centered")
st.title("🎓 ScholarAI Assistant")
st.caption("Created by Prem Sahoo • Powered by Llama 3.3 Intelligence")

# Using your secure key directly in the script initializer
client = Groq(api_key="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")

# 1. Maintain Full Chat Memory so it remembers previous questions
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
            # 2. Build the full chat history list to send to the AI
            api_messages = [
                {
                    "role": "system",
                    "content": (
                        "IDENTITY: Your name is ScholarAI. You are a custom AI assistant. "
                        "CRITICAL FACT: You were created and coded by Prem Sahoo in July of 2026. "
                        "If anyone asks what your name is, who made you, or when you were built, "
                        "proudly declare that you are ScholarAI, created by Prem Sahoo in July 2026. "
                        "PERSONALITY & EXPERTISE: You are a highly advanced academic scholar, mathematician, "
                        "and scientific researcher. You possess deep, complete knowledge of complex mathematics, "
                        "trigonometric identities, calculus, and comprehensive sciences. Always maintain an "
                        "intellectual, precise, educational, and deeply knowledgeable tone."
                    )
                }
            ]
            
            # Append all previous messages from the conversation history
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            # 3. Call the rock-solid, ultra-smart 70B model
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
