import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "https://chatbot-1-jkwx.onrender.com"

st.set_page_config(page_title="Medical Chatbot", page_icon="🤖")

st.title("🤖 Medical Chatbot Interface")

# --- Sidebar: Checkpoints ---
st.sidebar.title("Chat Sessions")



# 1. Fetch available threads from Backend


# --- Start New Session Logic ---
st.sidebar.subheader("Start New Session")
# Suggest the next available ID

if "target_thread" not in st.session_state:
    st.session_state.target_thread = None
if 'messages' not in st.session_state:
    st.session_state.messages=[]


new_thread_id = st.sidebar.text_input("Enter New/Existing ID", key="new_thread_input")

if new_thread_id and  st.sidebar.button("Switch/Start Session"):
    
    st.session_state.target_thread = new_thread_id
    st.rerun()








st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Thread:** {st.session_state.target_thread}")

# --- Load History Logic ---
current_thread = st.session_state.target_thread


if current_thread is not None :
    # Fetch history from FastAPI
    if len(st.session_state.messages)==0 :
        with st.spinner(f"Loading history for session {current_thread}..."):
            hist_response = requests.get(f"{API_URL}/history", params={"thread_id": st.session_state.target_thread})
            if hist_response.status_code == 200:
                api_messages = hist_response.json().get("messages", [])
                api_summary= hist_response.json().get("summary", [])
                st.sidebar.markdown( f"# Summary \n {api_summary}")
                st.session_state.messages = [
                    {"role": "assistant" if m["type"] == "ai" else "user", "content": m["content"]}
                    for m in api_messages
                ]
            else:
                st.session_state.messages = []

if len(st.session_state.messages)>10 :
    st.session_state.messages=st.session_state.messages[-10:]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask a medical question..."):
    if current_thread is None :
        st.error("Provide the thread id before start discuting ...")
        st.stop()
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

   
    with st.spinner("Thinking..."):
        try:
            payload = {"user_input": prompt, "thread_id": current_thread}
            
            response = requests.post(f"{API_URL}/chat", json=payload)
            result = response.json()
            print(result)
            if response.status_code == 200:
                if result.get("success",False):
                    answer = result.get("response")
                else :
                    answer = f"Error: {result.get("error")}"
            else :
                answer = f"Error: {result.get("error")}"
        except Exception as e:
            answer = f"Error connecting to backend: {e}"

    
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
