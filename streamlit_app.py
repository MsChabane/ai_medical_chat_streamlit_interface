import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "https://ai-medical-chatbot-server.onrender.com/"

st.set_page_config(page_title="Medical Chatbot", page_icon="🤖")

st.title("🤖 Medical Chatbot Interface")

# --- Sidebar: Checkpoints ---
st.sidebar.title("Chat Sessions")



# 1. Fetch available threads from Backend
try:
    response = requests.get(f"{API_URL}/checkpoints")
    if response.status_code == 200:
        threads = response.json().get("threads", [])
    else:
        st.sidebar.error("Could not fetch sessions.")
        threads = []
except Exception as e:
    st.sidebar.error(f"Backend not reachable: {e}")
    threads = []

# --- Start New Session Logic ---
st.sidebar.subheader("Start New Session")
# Suggest the next available ID

if "all_thread_ids" not in st.session_state:
    st.session_state.all_thread_ids = [thread.get("thread_id") for thread in threads]

new_thread_id = st.sidebar.text_input("Enter New/Existing ID", key="new_thread_input")
if "target_thread" not in st.session_state:
    st.session_state.target_thread = threads[0].get("thread_id") if threads else None

if new_thread_id and  st.sidebar.button("Switch/Start Session"):
    
    st.session_state.target_thread = new_thread_id
    if new_thread_id not in st.session_state.all_thread_ids:

         st.session_state.all_thread_ids.append(new_thread_id)
    # Force a rerun to load the new history
    st.rerun()




selected_thread = st.sidebar.selectbox(
    "Select a Thread ID:", 
    options=st.session_state.all_thread_ids,

    index=st.session_state.all_thread_ids.index(st.session_state.target_thread) if st.session_state.target_thread in st.session_state.all_thread_ids else 0
)

# Update target if selectbox changes
if selected_thread and selected_thread != st.session_state.target_thread:
    st.session_state.target_thread = selected_thread
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Thread:** {st.session_state.target_thread}")

# --- Load History Logic ---
current_thread = st.session_state.target_thread


    # Fetch history from FastAPI
with st.spinner(f"Loading history for session {current_thread}..."):
    hist_response = requests.get(f"{API_URL}/history", params={"thread_id": st.session_state.target_thread})
    if hist_response.status_code == 200:
        api_messages = hist_response.json().get("messages", [])
        st.session_state.messages = [
            {"role": "assistant" if m["type"] == "ai" else "user", "content": m["content"]}
            for m in api_messages
        ]
    else:
        st.session_state.messages = []
        st.error("Failed to load history.")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask a medical question..."):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

   
    with st.spinner("Thinking..."):
        try:
            payload = {"user_input": prompt, "thread_id": current_thread}
            
            response = requests.post(f"{API_URL}/chat", json=payload)
            
            if response.status_code == 200:
                answer = response.json().get("response")
            else:
                answer = f"Error: {response.text}"
        except Exception as e:
            answer = f"Error connecting to backend: {e}"

    #
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})