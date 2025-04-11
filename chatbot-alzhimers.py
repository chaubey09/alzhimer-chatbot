import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import pandas as pd

# ----------------- Configuration -----------------
st.set_page_config(
    page_title="Alzheimer's Detection Chatbot", 
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)
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
        :root {
            --primary: #4a6fa5;
            --secondary: #166088;
            --accent: #4fc3f7;
            --light: #f8f9fa;
            --dark: #212529;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --info: #17a2b8;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f5f7fb;
            color: var(--dark);
            line-height: 1.6;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--secondary);
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Header Styling */
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            padding: 2rem;
            border-radius: 0 0 15px 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            color: white;
        }
        
        .header h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Card Styling */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border-left: 4px solid var(--accent);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        /* Button Styling */
        .stButton > button {
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.7rem 1.5rem;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            background-color: var(--secondary);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Sidebar Styling */
        .stSidebar {
            background: white;
            box-shadow: 5px 0 15px rgba(0, 0, 0, 0.05);
        }
        
        .sidebar .sidebar-content {
            padding: 1.5rem;
        }
        
        /* Navigation Buttons */
        .nav-btn {
            width: 100%;
            text-align: left;
            padding: 0.8rem 1.2rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-size: 1rem;
            font-weight: 500;
            background: transparent;
            color: var(--dark);
            border: none;
        }
        
        .nav-btn:hover {
            background-color: rgba(74, 111, 165, 0.1);
            color: var(--primary);
        }
        
        .nav-btn.active {
            background-color: var(--primary);
            color: white;
            font-weight: 600;
        }
        
        /* Progress Bar */
        .progress-container {
            width: 100%;
            background-color: #e9ecef;
            border-radius: 10px;
            margin: 1.5rem 0;
            height: 20px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--accent) 0%, var(--primary) 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.7rem;
            font-weight: bold;
        }
        
        /* Chat Bubbles */
        .user-bubble {
            background-color: var(--primary);
            color: white;
            border-radius: 18px 18px 0 18px;
            padding: 12px 16px;
            margin: 8px 0;
            max-width: 80%;
            align-self: flex-end;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .bot-bubble {
            background-color: white;
            color: var(--dark);
            border-radius: 18px 18px 18px 0;
            padding: 12px 16px;
            margin: 8px 0;
            max-width: 80%;
            align-self: flex-start;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            border: 1px solid #eee;
        }
        
        /* Status Indicators */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .status-pending {
            background-color: rgba(255, 193, 7, 0.1);
            color: #d39e00;
        }
        
        .status-completed {
            background-color: rgba(40, 167, 69, 0.1);
            color: #28a745;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input {
            border-radius: 8px;
            padding: 0.7rem 1rem;
            border: 1px solid #ced4da;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .card {
                padding: 1rem;
            }
            
            .nav-btn {
                padding: 0.6rem 1rem;
                font-size: 0.9rem;
            }
        }
        
        /* Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease forwards;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary);
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Header -----------------
st.markdown("""
    <div class="header">
        <h1>Alzheimer's Detection and Assistance Companion</h1>
        <p>Your personalized care management system for Alzheimer's support</p>
    </div>
""", unsafe_allow_html=True)

# ----------------- Sidebar Navigation -----------------
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: var(--primary);">🧭 Navigation</h2>
    </div>
""", unsafe_allow_html=True)

# Define pages with icons and descriptions
pages = {
    "Home": {"icon": "🏠", "desc": "Main dashboard and MRI analysis"},
    "Chatbot": {"icon": "💬", "desc": "Interactive AI assistant"},
    "Notifications": {"icon": "⏰", "desc": "Manage reminders and alerts"},
    "Medications": {"icon": "💊", "desc": "Medication schedule tracker"},
    "Cognitive Exercises": {"icon": "🧠", "desc": "Brain training activities"},
    "Emergency Contacts": {"icon": "🆘", "desc": "Important contact information"},
    "Health Tips": {"icon": "💡", "desc": "Personalized wellness advice"},
    "Progress Tracking": {"icon": "📈", "desc": "Monitor cognitive changes"},
    "Daily Summary": {"icon": "📋", "desc": "Daily checklist and progress"}
}

# Create enhanced navigation
selected_page = st.sidebar.radio(
    "Navigate to:",
    options=list(pages.keys()),
    format_func=lambda x: f"{pages[x]['icon']} {x}",
    label_visibility="collapsed"
)

# Add descriptions for each page
st.sidebar.markdown(f"""
    <div style="margin-top: 1.5rem; padding: 1rem; background-color: rgba(74, 111, 165, 0.05); border-radius: 10px;">
        <p style="font-size: 0.9rem; color: var(--secondary);">
            <strong>{pages[selected_page]['icon']} {selected_page}:</strong> {pages[selected_page]['desc']}
        </p>
    </div>
""", unsafe_allow_html=True)

# Add user profile section
st.sidebar.markdown(f"""
    <div style="margin-top: 2rem; padding: 1.5rem; background-color: white; border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);">
        <div style="display: flex; align-items: center; gap: 1.2rem; margin-bottom: 1.2rem;">
            <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #4a6fa5 0%, #166088 100%); 
                        display: flex; align-items: center; justify-content: center; color: white; font-size: 1.8rem;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">👤</div>
            <div>
                <h4 style="margin: 0; color: var(--dark); font-size: 1.1rem;">User Profile</h4>
                <p style="margin: 0; font-size: 0.9rem; color: var(--secondary); font-weight: 500;">Anmol Chaubey</p>
            </div>
        </div>
        <hr style="margin: 0.8rem 0; border: none; height: 1px; background: linear-gradient(90deg, rgba(74,111,165,0.1) 0%, rgba(74,111,165,0.3) 50%, rgba(74,111,165,0.1) 100%);">
        <div style="display: flex; flex-direction: column; gap: 0.6rem;">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 0.9rem; color: var(--secondary);"><strong>Patient ID:</strong></span>
                <span style="font-size: 0.9rem; color: var(--primary); font-weight: 500;">ALZ-24MAI0111</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 0.9rem; color: var(--secondary);"><strong>Last Activity:</strong></span>
                <span style="font-size: 0.9rem; color: var(--primary); font-weight: 500;">Today</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 0.9rem; color: var(--secondary);"><strong>Status:</strong></span>
                <span style="font-size: 0.9rem; color: var(--success); font-weight: 500; display: flex; align-items: center; gap: 0.3rem;">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="6" cy="6" r="5" fill="#28a745"/>
                    </svg>
                    Active
                </span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ----------------- Home Page -----------------
if selected_page == "Home":
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2>🧠 Brain Health Analysis</h2>
            <div class="status-indicator status-completed" style="margin-left: auto;">
                <span>Last scan: Today</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div class="card">
                <h3>Upload MRI Scan</h3>
                <p>Upload a brain MRI image for Alzheimer's detection analysis. Supported formats: JPG, PNG</p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_image = st.file_uploader("Choose an MRI image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded MRI Image", use_column_width=True)
            
            # Simulate processing animation
            with st.spinner("Analyzing MRI scan..."):
                import time
                time.sleep(2)
                
                # Dummy model prediction
                prediction = "VeryMildDemented"
                st.session_state.last_prediction = prediction
                
                if prediction == "VeryMildDemented":
                    explanation = """
                    <div class="card fade-in" style="margin-top: 1.5rem;">
                        <h4>Analysis Results</h4>
                        <div class="status-indicator status-pending">
                            <span>Very Mild Dementia Detected</span>
                        </div>
                        <p style="margin-top: 1rem;">This suggests the patient may be in the <strong>early stage of Alzheimer's disease</strong>, 
                        often associated with <strong>Mild Cognitive Impairment (MCI)</strong>. Individuals at this stage might have slight 
                        memory issues but generally maintain independence.</p>
                        <p><strong>Recommendation:</strong> Consult a neurologist for a full diagnosis and consider cognitive exercises 
                        to maintain brain health.</p>
                    </div>
                    """
                elif prediction == "MildDemented":
                    explanation = """
                    <div class="card fade-in" style="margin-top: 1.5rem;">
                        <h4>Analysis Results</h4>
                        <div class="status-indicator status-warning">
                            <span>Mild Dementia Detected</span>
                        </div>
                        <p style="margin-top: 1rem;">This indicates an <strong>early stage of dementia</strong>, where memory loss 
                        and confusion may start to impact daily life.</p>
                        <p><strong>Recommendation:</strong> Medical evaluation is recommended to confirm and plan further steps. 
                        Consider setting up medication reminders and cognitive exercises.</p>
                    </div>
                    """
                elif prediction == "ModerateDemented":
                    explanation = """
                    <div class="card fade-in" style="margin-top: 1.5rem;">
                        <h4>Analysis Results</h4>
                        <div class="status-indicator status-danger">
                            <span>Moderate Dementia Detected</span>
                        </div>
                        <p style="margin-top: 1rem;">This reflects a <strong>moderate stage of Alzheimer's disease</strong>, often 
                        characterized by noticeable confusion, increased memory loss, and need for assistance with routine tasks.</p>
                        <p><strong>Recommendation:</strong> A comprehensive care plan may be needed. Ensure emergency contacts 
                        are up to date and consider professional care options.</p>
                    </div>
                    """
                else:
                    explanation = """
                    <div class="card fade-in" style="margin-top: 1.5rem;">
                        <h4>Analysis Results</h4>
                        <div class="status-indicator status-completed">
                            <span>No Dementia Detected</span>
                        </div>
                        <p style="margin-top: 1rem;">No signs of dementia are visible in the MRI scan.</p>
                        <p><strong>Recommendation:</strong> Maintain a healthy lifestyle with regular exercise and cognitive 
                        activities to support brain health.</p>
                    </div>
                    """
                
                st.markdown(explanation, unsafe_allow_html=True)
                
                if not st.session_state.chat_history or st.session_state.chat_history[-1]["content"] != explanation:
                    st.session_state.chat_history.append({
                        "role": "bot",
                        "content": explanation
                    })
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3>Quick Actions</h3>
                <div style="display: flex; flex-direction: column; gap: 0.8rem; margin-top: 1rem;">
                    <button class="nav-btn" onclick="window.location.href='#chatbot'">
                        💬 Ask About Results
                    </button>
                    <button class="nav-btn" onclick="window.location.href='#medications'">
                        💊 Add Medication
                    </button>
                    <button class="nav-btn" onclick="window.location.href='#exercises'">
                        🧠 Start Exercise
                    </button>
                    <button class="nav-btn" onclick="window.location.href='#contacts'">
                        🆘 Update Contacts
                    </button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="card" style="margin-top: 1.5rem;">
                <h3>Daily Checklist</h3>
                <div style="margin-top: 1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0;">
                        <span>💊 Medications</span>
                        <span style="color: var(--success);">✓</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0;">
                        <span>🧠 Exercises</span>
                        <span style="color: var(--danger);">✗</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0;">
                        <span>📞 Contacts</span>
                        <span style="color: var(--success);">✓</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0;">
                        <span>📊 Progress</span>
                        <span style="color: var(--danger);">✗</span>
                    </div>
                </div>
                <button class="nav-btn" style="margin-top: 1rem; background-color: var(--primary); color: white;">
                    View Full Summary
                </button>
            </div>
        """, unsafe_allow_html=True)

# ----------------- Chatbot Page -----------------
elif selected_page == "Chatbot":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>💬 Alzheimer's Companion</h2>
            <div class="status-indicator status-completed">
                <span>Online</span>
            </div>
        </div>
        <div class="card">
            <p>Ask questions about Alzheimer's disease, your MRI results, caregiving tips, or general brain health.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            st.markdown("### Conversation History")
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                        <div class="user-bubble">
                            {msg["content"]}
                        </div>
                    """, unsafe_allow_html=True)
                elif msg["role"] == "bot":
                    st.markdown(f"""
                        <div class="bot-bubble">
                            {msg["content"]}
                        </div>
                    """, unsafe_allow_html=True)
    
    # Chat input at the bottom
    user_input = st.chat_input("Type your question here...", key="chat_input")
    
    if user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Update chat display immediately
        with chat_container:
            st.markdown(f"""
                <div class="user-bubble">
                    {user_input}
                </div>
            """, unsafe_allow_html=True)
        
        # Generate response
        with st.spinner("Thinking..."):
            try:
                # Include context if available
                if "last_prediction" in st.session_state and st.session_state.last_prediction:
                    context = f"Based on the previous MRI analysis showing {st.session_state.last_prediction}, "
                else:
                    context = ""
                
                response = model.generate_content(context + user_input)
                bot_reply = response.text
            except Exception as e:
                bot_reply = f"Sorry, I encountered an error. Please try again later. Error: {str(e)}"
            
            st.session_state.chat_history.append({
                "role": "bot",
                "content": bot_reply
            })
            
            # Update chat display with bot response
            with chat_container:
                st.markdown(f"""
                    <div class="bot-bubble">
                        {bot_reply}
                    </div>
                """, unsafe_allow_html=True)

# ----------------- Notifications Page -----------------
elif selected_page == "Notifications":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>⏰ Reminders & Alerts</h2>
            <div class="status-indicator status-completed">
                <span>Active</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("notification_form"):
            st.markdown("""
                <div class="card">
                    <h3>Create New Reminder</h3>
            """, unsafe_allow_html=True)
            
            notification_time = st.time_input("Time", value=datetime.time(8, 0))
            notification_message = st.text_input("Message", placeholder="E.g., Take morning medication")
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Weekdays", "Weekends", "Custom"])
            
            submitted = st.form_submit_button("Add Reminder", type="primary")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                st.session_state.notifications.append({
                    "time": notification_time,
                    "message": notification_message,
                    "frequency": frequency,
                    "active": True
                })
                st.session_state.daily_summary["notifications_checked"] = True
                st.success("Reminder added successfully!")
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3>Your Reminders</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.notifications:
            for i, notification in enumerate(st.session_state.notifications):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"""
                        <div style="padding: 0.5rem 0;">
                            <p style="margin: 0; font-weight: 500;">⏰ {notification['time'].strftime('%I:%M %p')}</p>
                            <p style="margin: 0; font-size: 0.9rem; color: var(--secondary);">{notification['message']}</p>
                            <p style="margin: 0; font-size: 0.8rem; color: var(--dark); opacity: 0.7;">{notification['frequency']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button("×", key=f"del_notif_{i}"):
                        st.session_state.notifications.pop(i)
                        st.experimental_rerun()
        
        else:
            st.markdown("""
                <div style="text-align: center; padding: 2rem 0; color: var(--secondary); opacity: 0.7;">
                    <p>No reminders set yet</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Medications Page -----------------
elif selected_page == "Medications":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>💊 Medication Management</h2>
            <div class="status-indicator status-completed">
                <span>{len(st.session_state.medications)} Medications</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("medication_form"):
            st.markdown("""
                <div class="card">
                    <h3>Add New Medication</h3>
            """, unsafe_allow_html=True)
            
            med_name = st.text_input("Medication Name", placeholder="E.g., Donepezil")
            med_dosage = st.number_input("Dosage (mg)", min_value=1, max_value=1000)
            med_time = st.time_input("Time to Take")
            med_frequency = st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily", "As needed"])
            med_notes = st.text_area("Special Instructions", placeholder="E.g., Take with food")
            
            submitted = st.form_submit_button("Add Medication", type="primary")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                st.session_state.medications.append({
                    "name": med_name,
                    "dosage": med_dosage,
                    "time": med_time,
                    "frequency": med_frequency,
                    "notes": med_notes,
                    "last_taken": None
                })
                st.session_state.daily_summary["medications_taken"] = True
                st.success(f"{med_name} added to your medication schedule!")
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3>Medication Schedule</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.medications:
            for i, med in enumerate(st.session_state.medications):
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"""
                        <div style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                            <p style="margin: 0; font-weight: 500;">{med['name']} <span style="font-size: 0.9rem; color: var(--secondary);">{med['dosage']}mg</span></p>
                            <p style="margin: 0; font-size: 0.9rem;">⏰ {med['time'].strftime('%I:%M %p')} • {med['frequency']}</p>
                            {f"<p style='margin: 0; font-size: 0.8rem; color: var(--secondary);'>📝 {med['notes']}</p>" if med['notes'] else ""}
                        </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button("✓", key=f"take_med_{i}"):
                        st.session_state.medications[i]["last_taken"] = datetime.datetime.now()
                        st.experimental_rerun()
        
        else:
            st.markdown("""
                <div style="text-align: center; padding: 2rem 0; color: var(--secondary); opacity: 0.7;">
                    <p>No medications added yet</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Cognitive Exercises Page -----------------
elif selected_page == "Cognitive Exercises":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>🧠 Cognitive Training</h2>
            <div class="status-indicator status-completed">
                <span>Daily Challenge</span>
            </div>
        </div>
        
        <div class="card">
            <h3>Memory Game</h3>
            <p>Try to remember the sequence of numbers shown below. This exercise helps improve short-term memory.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Start New Memory Game", type="primary"):
        import random
        numbers = [random.randint(1, 9) for _ in range(5)]
        st.session_state.memory_game_numbers = numbers
        st.session_state.memory_game_start_time = datetime.datetime.now()
        st.session_state.daily_summary["cognitive_exercises_completed"] = True
    
    if "memory_game_numbers" in st.session_state:
        st.markdown("""
            <div class="card">
                <h4>Remember these numbers:</h4>
                <div style="display: flex; gap: 1rem; justify-content: center; margin: 1rem 0;">
        """, unsafe_allow_html=True)
        
        for num in st.session_state.memory_game_numbers:
            st.markdown(f"""
                <div style="width: 50px; height: 50px; background-color: var(--primary); 
                            color: white; border-radius: 10px; display: flex; 
                            align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;">
                    {num}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        user_input = st.text_input("Enter the numbers you remember (separated by spaces):", 
                                 placeholder="e.g., 1 2 3 4 5")
        
        if st.button("Check Answer"):
            try:
                user_numbers = list(map(int, user_input.split()))
                if user_numbers == st.session_state.memory_game_numbers:
                    time_taken = (datetime.datetime.now() - st.session_state.memory_game_start_time).seconds
                    st.success(f"""
                        🎉 Correct! You remembered all numbers in {time_taken} seconds!
                        <div style="margin-top: 1rem; font-size: 0.9rem;">
                            Difficulty: {"Easy" if time_taken < 15 else "Moderate" if time_taken < 30 else "Challenging"}
                        </div>
                    """)
                else:
                    st.error(f"""
                        ❌ Not quite right. The correct numbers were: {st.session_state.memory_game_numbers}
                        <div style="margin-top: 1rem;">
                            Try again or start a new game.
                        </div>
                    """)
            except ValueError:
                st.error("Please enter numbers separated by spaces (e.g., 1 2 3 4 5)")

# ----------------- Emergency Contacts Page -----------------
elif selected_page == "Emergency Contacts":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>🆘 Emergency Contacts</h2>
            <div class="status-indicator status-completed">
                <span>{len(st.session_state.emergency_contacts)} Contacts</span>
            </div>
        </div>
        
        <div class="card">
            <p>Add emergency contacts who should be notified in case of urgent situations.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("contact_form"):
            st.markdown("""
                <div class="card">
                    <h3>Add New Contact</h3>
            """, unsafe_allow_html=True)
            
            contact_name = st.text_input("Name", placeholder="E.g., Dr. Smith")
            contact_phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
            contact_relation = st.selectbox("Relationship", 
                                          ["Doctor", "Family Member", "Caregiver", "Friend", "Neighbor", "Other"])
            contact_priority = st.select_slider("Priority", ["Low", "Medium", "High"], value="Medium")
            
            submitted = st.form_submit_button("Add Contact", type="primary")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                st.session_state.emergency_contacts.append({
                    "name": contact_name,
                    "phone": contact_phone,
                    "relation": contact_relation,
                    "priority": contact_priority
                })
                st.session_state.daily_summary["emergency_contacts_updated"] = True
                st.success(f"{contact_name} added to emergency contacts!")
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3>Your Contacts</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.emergency_contacts:
            for i, contact in enumerate(st.session_state.emergency_contacts):
                priority_color = {
                    "High": "var(--danger)",
                    "Medium": "var(--warning)",
                    "Low": "var(--success)"
                }.get(contact["priority"], "var(--secondary)")
                
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"""
                        <div style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                            <p style="margin: 0; font-weight: 500;">{contact['name']}</p>
                            <p style="margin: 0; font-size: 0.9rem;">📞 {contact['phone']}</p>
                            <p style="margin: 0; font-size: 0.8rem; color: var(--secondary);">
                                {contact['relation']} • 
                                <span style="color: {priority_color};">{contact['priority']} priority</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button("✕", key=f"del_contact_{i}"):
                        st.session_state.emergency_contacts.pop(i)
                        st.experimental_rerun()
        
        else:
            st.markdown("""
                <div style="text-align: center; padding: 2rem 0; color: var(--secondary); opacity: 0.7;">
                    <p>No emergency contacts added yet</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Emergency button
    st.markdown("""
        <div style="position: fixed; bottom: 2rem; right: 2rem;">
            <button style="background-color: var(--danger); color: white; border: none; 
                        border-radius: 50%; width: 60px; height: 60px; font-size: 1.2rem;
                        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4); cursor: pointer;
                        transition: all 0.3s ease;">
                🆘
            </button>
        </div>
    """, unsafe_allow_html=True)

# ----------------- Health Tips Page -----------------
elif selected_page == "Health Tips":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>💡 Health & Wellness Tips</h2>
            <div class="status-indicator status-completed">
                <span>Personalized</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.last_prediction:
        if st.session_state.last_prediction == "VeryMildDemented":
            tips = [
                {
                    "title": "Stay Socially Active",
                    "icon": "👥",
                    "content": "Regular social interaction can help maintain cognitive function. Consider joining a club or group activity.",
                    "category": "Lifestyle"
                },
                {
                    "title": "Mediterranean Diet",
                    "icon": "🥗",
                    "content": "A diet rich in fruits, vegetables, whole grains, olive oil, and fish may help slow cognitive decline.",
                    "category": "Nutrition"
                },
                {
                    "title": "Regular Exercise",
                    "icon": "🏃‍♂️",
                    "content": "Aim for at least 30 minutes of moderate exercise most days. Walking, swimming, and yoga are excellent choices.",
                    "category": "Physical Health"
                },
                {
                    "title": "Cognitive Stimulation",
                    "icon": "🧩",
                    "content": "Engage in puzzles, reading, or learning new skills to keep your brain active and challenged.",
                    "category": "Mental Health"
                },
                {
                    "title": "Sleep Hygiene",
                    "icon": "🛌",
                    "content": "Maintain a regular sleep schedule and create a restful environment to support memory consolidation.",
                    "category": "Lifestyle"
                },
                {
                    "title": "Stress Management",
                    "icon": "🧘‍♀️",
                    "content": "Practice relaxation techniques like deep breathing or meditation to reduce stress, which can impact cognition.",
                    "category": "Mental Health"
                }
            ]
        elif st.session_state.last_prediction == "MildDemented":
            tips = [
                {
                    "title": "Routine Establishment",
                    "icon": "📅",
                    "content": "Maintain a consistent daily routine to reduce confusion and provide structure.",
                    "category": "Lifestyle"
                },
                {
                    "title": "Memory Aids",
                    "icon": "📝",
                    "content": "Use calendars, notes, and reminder systems to help with daily tasks and appointments.",
                    "category": "Tools"
                },
                {
                    "title": "Safe Environment",
                    "icon": "🏠",
                    "content": "Remove tripping hazards and consider safety modifications like grab bars in bathrooms.",
                    "category": "Safety"
                },
                {
                    "title": "Simplify Tasks",
                    "icon": "✂️",
                    "content": "Break down complex tasks into smaller, manageable steps to reduce frustration.",
                    "category": "Strategies"
                },
                {
                    "title": "Therapeutic Activities",
                    "icon": "🎨",
                    "content": "Engage in art, music, or reminiscence therapy which can be calming and stimulating.",
                    "category": "Mental Health"
                },
                {
                    "title": "Caregiver Support",
                    "icon": "🤝",
                    "content": "Consider joining a support group for caregivers to share experiences and coping strategies.",
                    "category": "Support"
                }
            ]
        else:
            tips = [
                {
                    "title": "Brain-Healthy Nutrition",
                    "icon": "🍎",
                    "content": "Focus on antioxidant-rich foods like berries, leafy greens, and nuts to support brain health.",
                    "category": "Nutrition"
                },
                {
                    "title": "Regular Check-ups",
                    "icon": "🩺",
                    "content": "Schedule regular medical check-ups to monitor overall health and cognitive function.",
                    "category": "Healthcare"
                },
                {
                    "title": "Mental Stimulation",
                    "icon": "📚",
                    "content": "Challenge your brain with new learning experiences, puzzles, or memory games.",
                    "category": "Mental Health"
                },
                {
                    "title": "Physical Activity",
                    "icon": "🚶‍♂️",
                    "content": "Regular physical activity improves blood flow to the brain and may help maintain cognitive function.",
                    "category": "Physical Health"
                },
                {
                    "title": "Social Engagement",
                    "icon": "👨‍👩‍👧‍👦",
                    "content": "Stay connected with friends and family to maintain emotional well-being and cognitive stimulation.",
                    "category": "Social"
                },
                {
                    "title": "Sleep Quality",
                    "icon": "😴",
                    "content": "Prioritize good sleep habits as quality sleep helps with memory consolidation and brain health.",
                    "category": "Lifestyle"
                }
            ]
        
        # Display tips in a grid
        cols = st.columns(2)
        for i, tip in enumerate(tips):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class="card" style="margin-bottom: 1rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                            <div style="font-size: 1.5rem;">{tip['icon']}</div>
                            <h4 style="margin: 0;">{tip['title']}</h4>
                        </div>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;">{tip['content']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.8rem; color: var(--secondary);">{tip['category']}</span>
                            <button style="background: none; border: none; color: var(--primary); cursor: pointer; font-size: 0.8rem;">
                                More Info
                            </button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Upload an MRI image to get personalized health tips.")

# ----------------- Progress Tracking Page -----------------
elif selected_page == "Progress Tracking":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>📈 Cognitive Progress Tracking</h2>
            <div class="status-indicator status-completed">
                <span>{len(st.session_state.progress)} Records</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("progress_form"):
            st.markdown("""
                <div class="card">
                    <h3>Log Daily Progress</h3>
            """, unsafe_allow_html=True)
            
            progress_date = st.date_input("Date", value=datetime.date.today())
            progress_score = st.slider("Cognitive Score", min_value=0, max_value=100, value=75)
            mood = st.select_slider("Mood", ["😞", "🙁", "😐", "🙂", "😊"], value="😐")
            notes = st.text_area("Notes", placeholder="Any observations or comments...")
            
            submitted = st.form_submit_button("Save Entry", type="primary")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                st.session_state.progress.append({
                    "date": progress_date,
                    "score": progress_score,
                    "mood": mood,
                    "notes": notes
                })
                st.session_state.daily_summary["progress_logged"] = True
                st.success("Progress logged successfully!")
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3>Progress Over Time</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.progress:
            # Create DataFrame for visualization
            progress_df = pd.DataFrame(st.session_state.progress)
            progress_df['date'] = pd.to_datetime(progress_df['date'])
            
            # Line chart for cognitive score
            st.line_chart(progress_df.set_index('date')['score'], use_container_width=True)
            
            # Display recent entries
            st.markdown("### Recent Entries")
            for entry in sorted(st.session_state.progress, key=lambda x: x['date'], reverse=True)[:3]:
                st.markdown(f"""
                    <div style="padding: 0.8rem; margin: 0.5rem 0; background-color: #f8f9fa; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>{entry['date'].strftime('%b %d, %Y')}</strong>
                            <span style="font-size: 1.2rem;">{entry['mood']}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0;">
                            <div style="font-size: 0.9rem;">Score: <strong>{entry['score']}/100</strong></div>
                        </div>
                        {f"<div style='font-size: 0.9rem; color: var(--secondary);'>{entry['notes']}</div>" if entry['notes'] else ""}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; padding: 2rem 0; color: var(--secondary); opacity: 0.7;">
                    <p>No progress data recorded yet</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Daily Summary Page -----------------
elif selected_page == "Daily Summary":
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <h2>📋 Daily Summary</h2>
            <div class="status-indicator status-completed">
                <span>{datetime.date.today().strftime('%b %d, %Y')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    total_tasks = len(st.session_state.daily_summary)
    completed_tasks = sum(st.session_state.daily_summary.values())
    progress_percent = int((completed_tasks / total_tasks) * 100)
    
    st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Daily Completion</span>
                <span>{progress_percent}%</span>
            </div>
            <div style="width: 100%; height: 10px; background-color: #e9ecef; border-radius: 5px; overflow: hidden;">
                <div style="width: {progress_percent}%; height: 100%; background: linear-gradient(90deg, var(--accent) 0%, var(--primary) 100%);"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Task cards
    tasks = [
        {
            "key": "notifications_checked",
            "title": "⏰ Notifications",
            "description": "Review and respond to daily reminders",
            "icon": "🔔"
        },
        {
            "key": "medications_taken",
            "title": "💊 Medications",
            "description": "Take all scheduled medications",
            "icon": "💊"
        },
        {
            "key": "cognitive_exercises_completed",
            "title": "🧠 Cognitive Exercises",
            "description": "Complete daily brain training",
            "icon": "🧩"
        },
        {
            "key": "emergency_contacts_updated",
            "title": "📞 Emergency Contacts",
            "description": "Verify contact information",
            "icon": "📱"
        },
        {
            "key": "progress_logged",
            "title": "📊 Progress Tracking",
            "description": "Record daily cognitive status",
            "icon": "📈"
        }
    ]
    
    for task in tasks:
        is_completed = st.session_state.daily_summary[task["key"]]
        
        if is_completed:
            task_html = f"""
            <div class="card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 1.5rem;">{task['icon']}</div>
                        <div>
                            <h4 style="margin: 0;">{task['title']}</h4>
                            <p style="margin: 0; font-size: 0.9rem; color: var(--secondary);">{task['description']}</p>
                        </div>
                    </div>
                    <div>
                        <span style="color: var(--success); font-size: 1.2rem;">✓</span>
                    </div>
                </div>
            </div>
            """
        else:
            task_html = f"""
            <div class="card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 1.5rem;">{task['icon']}</div>
                        <div>
                            <h4 style="margin: 0;">{task['title']}</h4>
                            <p style="margin: 0; font-size: 0.9rem; color: var(--secondary);">{task['description']}</p>
                        </div>
                    </div>
                    <div>
                        <button onclick="window.location.href='#{task['key']}'" 
                                style="background-color: var(--primary); color: white; border: none; 
                                       border-radius: 5px; padding: 0.5rem 1rem; cursor: pointer;">
                            Mark Complete
                        </button>
                    </div>
                </div>
            </div>
            """
        
        st.markdown(task_html, unsafe_allow_html=True)
    
    # Daily reflection
    st.markdown("""
        <div class="card">
            <h3>Daily Reflection</h3>
            <p style="margin-bottom: 1rem;">Take a moment to reflect on your day:</p>
            <textarea style="width: 100%; min-height: 100px; border-radius: 8px; padding: 0.8rem; border: 1px solid #ced4da;"></textarea>
            <button style="background-color: var(--primary); color: white; border: none; 
                        border-radius: 8px; padding: 0.7rem 1.5rem; margin-top: 1rem; cursor: pointer;">
                Save Reflection
            </button>
        </div>
    """, unsafe_allow_html=True)

# ----------------- Footer -----------------
st.markdown("""
    <footer style="margin-top: 5rem; padding: 2rem 0; text-align: center; color: var(--secondary); border-top: 1px solid #eee;">
        <p style="margin: 0.5rem 0;">Developed with ❤️ by Anmol | 24MAI0111</p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem;">For support: <a href="mailto:anmolchaubey820@gmail.com" style="color: var(--primary); text-decoration: none;">anmolchaubey820@gmail.com</a></p>
        <p style="margin: 0.5rem 0; font-size: 0.8rem;">© 2023 Alzheimer's Companion. All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)
