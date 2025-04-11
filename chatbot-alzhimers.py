import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import pandas as pd

# ----------------- Configuration -----------------
st.set_page_config(page_title="Alzheimer's Detection Chatbot", page_icon="🧠")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

# ----------------- Session State Initialization -----------------
if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, list):
    st.session_state.chat_history = []

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

if "notifications" not in st.session_state:
    st.session_state.notifications = []

if "medications" not in st.session_state:
    st.session_state.medications = []

if "emergency_contacts" not in st.session_state:
    st.session_state.emergency_contacts = []

if "progress" not in st.session_state:
    st.session_state.progress = []

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

# ----------------- Notifications -----------------
st.subheader("⏰ Set Up Notifications")
notification_time = st.time_input("Set Notification Time", value=datetime.time(8, 0))
notification_message = st.text_input("Enter Notification Message", value="Time to take your medication!")

if st.button("Add Notification"):
    st.session_state.notifications.append({
        "time": notification_time,
        "message": notification_message
    })
    st.success(f"Notification added for {notification_time.strftime('%I:%M %p')}!")

# Check and display notifications
current_time = datetime.datetime.now().time()
for notification in st.session_state.notifications:
    if current_time.hour == notification["time"].hour and current_time.minute == notification["time"].minute:
        st.warning(f"🔔 Reminder: {notification['message']}")

# ----------------- Medication Reminders -----------------
st.subheader("💊 Medication Reminders")
med_name = st.text_input("Medication Name")
med_time = st.time_input("Medication Time")
med_dosage = st.number_input("Dosage (mg)", min_value=1, max_value=1000)

if st.button("Add Medication"):
    st.session_state.medications.append({
        "name": med_name,
        "time": med_time,
        "dosage": med_dosage
    })
    st.success(f"Added {med_name} to your medication list!")

# Display medication reminders
st.markdown("### 📋 Your Medication Schedule")
for med in st.session_state.medications:
    st.markdown(f"- **{med['name']}**: {med['dosage']} mg at {med['time'].strftime('%I:%M %p')}")

# ----------------- Cognitive Exercises -----------------
st.subheader("🧠 Cognitive Exercises")

# Example: Memory Game
if st.button("Start Memory Game"):
    import random
    numbers = [random.randint(1, 100) for _ in range(5)]
    st.write("Memorize these numbers:", numbers)
    st.session_state.memory_game_numbers = numbers

if "memory_game_numbers" in st.session_state:
    user_input = st.text_input("Enter the numbers you remember (comma-separated):")
    if st.button("Submit"):
        try:
            user_numbers = list(map(int, user_input.split(",")))
            if user_numbers == st.session_state.memory_game_numbers:
                st.success("🎉 Great job! You remembered all the numbers!")
            else:
                st.error(f"❌ Try again! The correct numbers were: {st.session_state.memory_game_numbers}")
        except ValueError:
            st.error("Please enter valid numbers separated by commas.")

# ----------------- Emergency Contacts -----------------
st.subheader("📞 Emergency Contacts")
contact_name = st.text_input("Contact Name")
contact_phone = st.text_input("Phone Number")

if st.button("Add Emergency Contact"):
    st.session_state.emergency_contacts.append({
        "name": contact_name,
        "phone": contact_phone
    })
    st.success(f"Added {contact_name} to your emergency contacts!")

# Display emergency contacts
st.markdown("### 📞 Your Emergency Contacts")
for contact in st.session_state.emergency_contacts:
    st.markdown(f"- **{contact['name']}**: {contact['phone']}")

# Simulate an emergency alert
if st.button("Trigger Emergency Alert"):
    for contact in st.session_state.emergency_contacts:
        st.warning(f"🚨 Emergency alert sent to {contact['name']} at {contact['phone']}!")

# ----------------- Personalized Health Tips -----------------
st.subheader("💡 Personalized Health Tips")

if st.session_state.last_prediction:
    if st.session_state.last_prediction == "VeryMildDemented":
        tips = [
            "Stay socially active to maintain cognitive function.",
            "Engage in regular physical activity like walking or yoga.",
            "Consult a neurologist for early intervention."
        ]
    elif st.session_state.last_prediction == "MildDemented":
        tips = [
            "Follow a Mediterranean diet rich in fruits, vegetables, and omega-3 fatty acids.",
            "Keep a consistent routine to reduce confusion.",
            "Consider cognitive therapy sessions."
        ]
    elif st.session_state.last_prediction == "ModerateDemented":
        tips = [
            "Ensure proper supervision during daily activities.",
            "Use memory aids like calendars and reminders.",
            "Plan for long-term care options."
        ]
    else:
        tips = [
            "Maintain a healthy lifestyle to prevent cognitive decline.",
            "Stay mentally active with puzzles and reading.",
            "Schedule regular check-ups with your doctor."
        ]

    st.markdown("### 🌟 Based on your MRI results:")
    for tip in tips:
        st.markdown(f"- {tip}")
else:
    st.info("Upload an MRI image to get personalized health tips.")

# ----------------- Progress Tracking -----------------
st.subheader("📊 Track Your Progress")
progress_date = st.date_input("Date")
progress_score = st.number_input("Cognitive Test Score", min_value=0, max_value=100)

if st.button("Log Progress"):
    st.session_state.progress.append({
        "date": progress_date,
        "score": progress_score
    })
    st.success("Progress logged successfully!")

# Display progress chart
if st.session_state.progress:
    progress_df = pd.DataFrame(st.session_state.progress)
    st.line_chart(progress_df.set_index("date"))

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
