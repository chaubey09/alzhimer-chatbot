import streamlit as st
import google.generativeai as genai
from PIL import Image

# ----------------- Configuration -----------------
st.set_page_config(page_title="Alzheimer's Detection Chatbot", page_icon="🧠")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

# ----------------- Session State -----------------
if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, list):
    st.session_state.chat_history = []

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

# ----------------- App Title -----------------
st.title("🧠 Alzheimer's Detection Chatbot by Anmol 24MAI0111")

# ----------------- Image Upload and Prediction -----------------
uploaded_image = st.file_uploader("Upload an MRI Image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded MRI Image", use_column_width=True)

    # Dummy model prediction — replace with actual model output in production
    prediction = "VeryMildDemented"

    # Store prediction for context retention
    st.session_state.last_prediction = prediction

    # Response based on prediction
    if prediction == "VeryMildDemented":
        explanation = (
            "🧠 You uploaded an MRI image.\n\n"
            "**Prediction:** `VeryMildDemented`\n\n"
            "This suggests the patient may be in the **early stage of Alzheimer's disease**, "
            "often associated with **Mild Cognitive Impairment (MCI)**. Individuals at this stage might have slight memory issues "
            "but generally maintain independence. A neurologist should be consulted for a full diagnosis."
        )
    elif prediction == "MildDemented":
        explanation = (
            "🧠 You uploaded an MRI image.\n\n"
            "**Prediction:** `MildDemented`\n\n"
            "This indicates an **early stage of dementia**, where memory loss and confusion may start to impact daily life. "
            "Medical evaluation is recommended to confirm and plan further steps."
        )
    elif prediction == "ModerateDemented":
        explanation = (
            "🧠 You uploaded an MRI image.\n\n"
            "**Prediction:** `ModerateDemented`\n\n"
            "This reflects a **moderate stage of Alzheimer's disease**, often characterized by noticeable confusion, "
            "increased memory loss, and need for assistance with routine tasks. A comprehensive care plan may be needed."
        )
    elif prediction == "NonDemented":
        explanation = (
            "🧠 You uploaded an MRI image.\n\n"
            "**Prediction:** `NonDemented`\n\n"
            "This suggests no signs of dementia are visible in the MRI. However, if there are symptoms, it’s best to consult a neurologist."
        )
    else:
        explanation = f"🧠 You uploaded an MRI image.\n\n**Prediction:** `{prediction}`"

    st.session_state.chat_history.append({
        "role": "bot",
        "content": explanation
    })

# ----------------- Chat Input -----------------
user_input = st.chat_input("Ask something about the model or prediction...")

if user_input:
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Optional context injection based on user's input
    if "last_prediction" in st.session_state and st.session_state.last_prediction:
        keywords = ["stage", "my alzheimer", "which stage", "how severe"]
        if any(kw in user_input.lower() for kw in keywords):
            contextual_msg = (
                f"Based on the MRI image you uploaded earlier, "
                f"the model predicted: `{st.session_state.last_prediction}`.\n\n"
            )
            # Add this to Gemini history explicitly
            gemini_history = [{"role": "user", "parts": [contextual_msg + user_input]}]
        else:
            gemini_history = [{"role": "user", "parts": [user_input]}]
    else:
        gemini_history = [{"role": "user", "parts": [user_input]}]

    # Prepare messages for Gemini
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

# ----------------- Chat History Display -----------------
if st.session_state.chat_history:
    st.markdown("### 💬 Chat History")
    for msg in st.session_state.chat_history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(f"🧑‍💬 **You:** {content}")
        elif role == "bot":
            st.markdown(f"🤖 **Bot:** {content}")
            
