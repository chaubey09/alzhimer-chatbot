import streamlit as st
import google.generativeai as genai
import PIL.Image

# Configure Gemini API securely using secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Load the Gemini model
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

# Initialize chat history
if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, list):
    st.session_state.chat_history = []

# Title
st.title("🧠 Alzheimer's Detection Chatbot")

# Image uploader
uploaded_image = st.file_uploader("Upload an MRI Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
if uploaded_image:
    st.image(uploaded_image, caption="Uploaded MRI Image", use_column_width=True)
    
    # Dummy model prediction — replace with your ML/DL model output
    prediction = "VeryMildDemented"
    bot_msg = f"🧠 You uploaded an MRI image.\n\n**Prediction:** `{prediction}`"
    
    st.session_state.chat_history.append({
        "role": "bot",
        "content": bot_msg
    })

# User chat input
user_input = st.chat_input("Ask something about the model or prediction...")
if user_input:
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Prepare messages for Gemini
    gemini_history = []
    for msg in st.session_state.chat_history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            gemini_role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": gemini_role, "parts": [msg["content"]]})

    try:
        response = model.generate_content(gemini_history)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"❌ Error from Gemini API: {str(e)}"

    st.session_state.chat_history.append({
        "role": "bot",
        "content": bot_reply
    })

# Display chat history
st.markdown("### 💬 Chat History")
for msg in st.session_state.chat_history:
    if isinstance(msg, dict) and "role" in msg and "content" in msg:
        if msg["role"] == "user":
            st.markdown(f"🧑‍💬 **You:** {msg['content']}")
        elif msg["role"] == "bot":
            st.markdown(f"🤖 **Bot:** {msg['content']}")