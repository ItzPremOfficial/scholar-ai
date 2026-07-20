import streamlit as st
from groq import Groq

st.set_page_config(page_title="ScholarAI", page_icon="🎓", layout="centered")
st.title("🎓 ScholarAI Assistant")
st.caption("Created by Prem Sahoo • Powered by Groq Engine")

client = Groq()

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
            response_stream = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "IDENTITY: Your name is ScholarAI. You are a custom AI assistant. "
                            "CRITICAL FACT: You were created and coded by Prem Sahoo in July of 2026. "
                            "If anyone asks what your name is, who made you, or when you were built, "
                            "proudly declare that you are ScholarAI, created by Prem Sahoo in July 2026. "
                            "PERSONALITY & EXPERTISE: Aside from this identity, you are a highly advanced academic scholar "
                            "and researcher. Your expertise covers complex mathematics, comprehensive sciences, and academic "
                            "subjects. You are also a journalist who relies heavily on verified, up-to-date facts. When a user "
                            "asks about current events or news, use your web search tool to find reliable facts. "
                            "Always maintain an intellectual, precise, educational, and deeply knowledgeable tone."
                        )
                    },
                    {"role": "user", "content": user_query}
                ],
                stream=True,
            )
            
            # This safely extracts the streaming text regardless of model structure variations
            for chunk in response_stream:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    # Check for standard streaming text format
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content') and choice.delta.content is not None:
                        full_response += choice.delta.content
                        response_placeholder.markdown(full_response + "▌")
                    # Fallback if the data comes back in an alternative dictionary/text layer
                    elif isinstance(choice, dict) and 'delta' in choice and 'content' in choice['delta']:
                        if choice['delta']['content'] is not None:
                            full_response += choice['delta']['content']
                            response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")
