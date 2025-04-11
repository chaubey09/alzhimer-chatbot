import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import pandas as pd

# ----------------- Configuration -----------------
st.set_page_config(page_title="Alzheimer's Detection Chatbot", page_icon="🤝")
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

if "daily_summary" not in st.session_state:
    st.session_state.daily_summary = {
        "notifications_checked": False,
        "medications_taken": False,
        "cognitive_exercises_completed": False,
        "emergency_contacts_updated": False,
        "progress_logged": False
    }

# ----------------- Custom CSS for Enhanced UI -----------------
st.markdown("""
    <style>
        /* General Styling */
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
            color: #2c3e50;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            text-align: center;
        }
        .header {
            background: linear-gradient(135deg, #3498db, #2980b9);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: white;
            font-size: 28px;
        }
        /* Sidebar Styling */
        .sidebar .sidebar-content {
            background: #ecf0f1;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* Buttons */
        .mark-done-button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .mark-done-button:hover {
            background-color: #2980b9;
        }
        /* Sidebar Navigation */
        .stButton > button {
            width: 100%;
            text-align: left;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            transition: background-color 0.3s ease;
            font-size: 16px;
            font-weight: 500;
        }
        .stButton > button:hover {
            background-color: #dcdcdc;
        }
        .stButton > button.selected {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        /* Tooltips */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: black;
            color: #fff;
            text-align: center;
            border-radius: 5px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        /* Sticky Sidebar */
        .stSidebar {
            position: fixed;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            width: 250px; /* Adjust width as needed */
            padding-top: 60px; /* Space for header */
        }
        /* Responsive Design */
        @media (max-width: 768px) {
            .stSidebar {
                width: 100%; /* Full width on small screens */
                height: auto;
            }
            .stButton > button {
                font-size: 14px;
                padding: 8px;
            }
            .tooltip .tooltiptext {
                width: 100px; /* Smaller tooltips on small screens */
            }
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Header -----------------
st.markdown("""
    <div class="header">
        <h1>Alzheimer's Detection and Assistance Chatbot</h1>
        <p>Your trusted companion for managing Alzheimer's care.</p>
    </div>
""", unsafe_allow_html=True)

# ----------------- Sidebar Navigation -----------------
st.sidebar.title("🧭 Navigation")

# Define pages with icons
pages = {
    "Home": "🏠",
    "Chatbot": "💬",
    "Notifications": "🔔",
    "Medications": "💊",
    "Cognitive Exercises": "🧠",
    "Emergency Contacts": "📞",
    "Health Tips": "💡",
    "Progress Tracking": "📊",
    "Daily Summary": "📋"
}

# Tooltip CSS
tooltip_css = """
<style>
.tooltip {
    position: relative;
    display: inline-block;
    cursor: pointer;
}
.tooltip .tooltiptext {
    visibility: hidden;
    width: 120px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 5px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -60px;
    opacity: 0;
    transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
"""
st.markdown(tooltip_css, unsafe_allow_html=True)

# Create enhanced navigation with icons and tooltips
selected_page = None
for page_name, icon in pages.items():
    tooltip_text = f"Go to {page_name}"
    button_html = f"""
    <div class="tooltip">
        <button style="width: 100%; text-align: left; padding: 10px; margin: 5px 0; border-radius: 5px; transition: background-color 0.3s ease;">
            {icon} {page_name}
        </button>
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    """
    if st.sidebar.button(f"{icon} {page_name}", key=page_name):
        selected_page = page_name

# Set the active page
if selected_page:
    page = selected_page
else:
    page = "Home"  # Default to Home


# ----------------- Home Page -----------------
if page == "Home":
    st.write("Welcome to the Alzheimer's Detection and Assistance Chatbot!")
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
                " You uploaded an MRI image.\n\n"
                "**Prediction:** `VeryMildDemented`\n\n"
                "This suggests the patient may be in the **early stage of Alzheimer's disease**, "
                "often associated with **Mild Cognitive Impairment (MCI)**. Individuals at this stage might have slight memory issues "
                "but generally maintain independence. A neurologist should be consulted for a full diagnosis."
            )
        elif prediction == "MildDemented":
            explanation = (
                "You uploaded an MRI image.\n\n"
                "**Prediction:** `MildDemented`\n\n"
                "This indicates an **early stage of dementia**, where memory loss and confusion may start to impact daily life. "
                "Medical evaluation is recommended to confirm and plan further steps."
            )
        elif prediction == "ModerateDemented":
            explanation = (
                "You uploaded an MRI image.\n\n"
                "**Prediction:** `ModerateDemented`\n\n"
                "This reflects a **moderate stage of Alzheimer's disease**, often characterized by noticeable confusion, "
                "increased memory loss, and need for assistance with routine tasks. A comprehensive care plan may be needed."
            )
        elif prediction == "NonDemented":
            explanation = (
                "You uploaded an MRI image.\n\n"
                "**Prediction:** `NonDemented`\n\n"
                "This suggests no signs of dementia are visible in the MRI. However, if there are symptoms, it’s best to consult a neurologist."
            )
        else:
            explanation = f"You uploaded an MRI image.\n\n**Prediction:** `{prediction}`"

        # Avoid appending duplicate responses
        if not st.session_state.chat_history or st.session_state.chat_history[-1]["content"] != explanation:
            st.session_state.chat_history.append({
                "role": "bot",
                "content": explanation
            })

# ----------------- Chatbot Page -----------------
elif page == "Chatbot":
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

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")
        for msg in st.session_state.chat_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                st.markdown(f"🧑‍💬 **You:** {content}")
            elif role == "bot":
                st.markdown(f"🤖 **Bot:** {content}")

# ----------------- Notifications Page -----------------
elif page == "Notifications":
    st.subheader("⏰ Set Up Notifications")
    notification_time = st.time_input("Set Notification Time", value=datetime.time(8, 0))
    notification_message = st.text_input("Enter Notification Message", value="Time to take your medication!")

    if st.button("Add Notification"):
        st.session_state.notifications.append({
            "time": notification_time,
            "message": notification_message
        })
        st.success(f"Notification added for {notification_time.strftime('%I:%M %p')}!")
        st.session_state.daily_summary["notifications_checked"] = True

    # Check and display notifications
    current_time = datetime.datetime.now().time()
    for notification in st.session_state.notifications:
        if current_time.hour == notification["time"].hour and current_time.minute == notification["time"].minute:
            st.warning(f"🔔 Reminder: {notification['message']}")

# ----------------- Medications Page -----------------
elif page == "Medications":
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
        st.session_state.daily_summary["medications_taken"] = True

    # Display medication reminders
    st.markdown("### 📋 Your Medication Schedule")
    for med in st.session_state.medications:
        st.markdown(f"- **{med['name']}**: {med['dosage']} mg at {med['time'].strftime('%I:%M %p')}")

# ----------------- Cognitive Exercises Page -----------------
elif page == "Cognitive Exercises":
    st.subheader("Cognitive Exercises")

    if st.button("Start Memory Game"):
        import random
        numbers = [random.randint(1, 100) for _ in range(5)]
        st.write("Memorize these numbers:", numbers)
        st.session_state.memory_game_numbers = numbers
        st.session_state.daily_summary["cognitive_exercises_completed"] = True

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

# ----------------- Emergency Contacts Page -----------------
elif page == "Emergency Contacts":
    st.subheader("📞 Emergency Contacts")
    contact_name = st.text_input("Contact Name")
    contact_phone = st.text_input("Phone Number")

    if st.button("Add Emergency Contact"):
        st.session_state.emergency_contacts.append({
            "name": contact_name,
            "phone": contact_phone
        })
        st.success(f"Added {contact_name} to your emergency contacts!")
        st.session_state.daily_summary["emergency_contacts_updated"] = True

    # Display emergency contacts
    st.markdown("### 📞 Your Emergency Contacts")
    for contact in st.session_state.emergency_contacts:
        st.markdown(f"- **{contact['name']}**: {contact['phone']}")

    # Simulate an emergency alert
    if st.button("Trigger Emergency Alert"):
        for contact in st.session_state.emergency_contacts:
            st.warning(f"🚨 Emergency alert sent to {contact['name']} at {contact['phone']}!")

# ----------------- Health Tips Page -----------------
elif page == "Health Tips":
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

# ----------------- Progress Tracking Page -----------------
elif page == "Progress Tracking":
    st.subheader("📊 Track Your Progress")
    progress_date = st.date_input("Date")
    progress_score = st.number_input("Cognitive Test Score", min_value=0, max_value=100)

    if st.button("Log Progress"):
        st.session_state.progress.append({
            "date": progress_date,
            "score": progress_score
        })
        st.success("Progress logged successfully!")
        st.session_state.daily_summary["progress_logged"] = True

    # Display progress chart
    if st.session_state.progress:
        progress_df = pd.DataFrame(st.session_state.progress)
        st.line_chart(progress_df.set_index("date"))

# ----------------- Daily Summary Page -----------------
elif page == "Daily Summary":
    st.subheader("📋 Daily Summary Checklist")

    # Function to calculate progress percentage
    def calculate_progress():
        total_tasks = len(st.session_state.daily_summary)
        completed_tasks = sum(st.session_state.daily_summary.values())
        return int((completed_tasks / total_tasks) * 100)

    # Progress Bar
    progress_percentage = calculate_progress()
    st.markdown(
        f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width: {progress_percentage}%;"></div>
        </div>
        <p style="text-align: center; margin-top: 10px;">Daily Progress: {progress_percentage}%</p>
        """,
        unsafe_allow_html=True
    )

    # Notifications
    col1, col2 = st.columns([3, 1])
    with col1:
        if not st.session_state.daily_summary["notifications_checked"]:
            st.markdown(
                """
                <div class="card">
                    <strong>📅 Notifications:</strong> 
                    <span class="red-cross">❌ Not Checked</span> yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="card">
                    <strong>📅 Notifications:</strong> 
                    <span class="green-check">✅ Checked</span> All notifications received today.
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if not st.session_state.daily_summary["notifications_checked"]:
            if st.button("Mark as Done", key="notifications"):
                st.session_state.daily_summary["notifications_checked"] = True
                st.experimental_rerun()

    # Medications
    col1, col2 = st.columns([3, 1])
    with col1:
        if not st.session_state.daily_summary["medications_taken"]:
            st.markdown(
                """
                <div class="card">
                    <strong>💊 Medications:</strong> 
                    <span class="red-cross">❌ Not Taken</span> yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="card">
                    <strong>💊 Medications:</strong> 
                    <span class="green-check">✅ Taken</span> All medications taken today.
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if not st.session_state.daily_summary["medications_taken"]:
            if st.button("Mark as Done", key="medications"):
                st.session_state.daily_summary["medications_taken"] = True
                st.experimental_rerun()

    # Cognitive Exercises
    col1, col2 = st.columns([3, 1])
    with col1:
        if not st.session_state.daily_summary["cognitive_exercises_completed"]:
            st.markdown(
                """
                <div class="card">
                    <strong>Cognitive Exercises:</strong> 
                    <span class="red-cross">❌ Not Completed</span> yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="card">
                    <strong>Cognitive Exercises:</strong> 
                    <span class="green-check">✅ Completed</span> Exercises completed today.
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if not st.session_state.daily_summary["cognitive_exercises_completed"]:
            if st.button("Mark as Done", key="cognitive_exercises"):
                st.session_state.daily_summary["cognitive_exercises_completed"] = True
                st.experimental_rerun()

    # Emergency Contacts
    col1, col2 = st.columns([3, 1])
    with col1:
        if not st.session_state.daily_summary["emergency_contacts_updated"]:
            st.markdown(
                """
                <div class="card">
                    <strong>📞 Emergency Contacts:</strong> 
                    <span class="red-cross">❌ Not Updated</span> yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="card">
                    <strong>📞 Emergency Contacts:</strong> 
                    <span class="green-check">✅ Updated</span> Contacts reviewed/updated today.
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if not st.session_state.daily_summary["emergency_contacts_updated"]:
            if st.button("Mark as Done", key="emergency_contacts"):
                st.session_state.daily_summary["emergency_contacts_updated"] = True
                st.experimental_rerun()

    # Progress Tracking
    col1, col2 = st.columns([3, 1])
    with col1:
        if not st.session_state.daily_summary["progress_logged"]:
            st.markdown(
                """
                <div class="card">
                    <strong>📊 Progress Tracking:</strong> 
                    <span class="red-cross">❌ Not Logged</span> yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="card">
                    <strong>📊 Progress Tracking:</strong> 
                    <span class="green-check">✅ Logged</span> Progress logged today.
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if not st.session_state.daily_summary["progress_logged"]:
            if st.button("Mark as Done", key="progress_tracking"):
                st.session_state.daily_summary["progress_logged"] = True
                st.experimental_rerun()

# ----------------- Footer -----------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px;">
        <p>Developed by Anmol | 24MAI0111</p>
        <p>Contact us at <a href="mailto:anmolchaubey820@gmail.com">anmolchaubey820@gmail.com</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
