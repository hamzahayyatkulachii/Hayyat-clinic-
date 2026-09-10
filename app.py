"""
Hayyat Clinic - Streamlit Version
Dr. Rasheed Ahmad | Mithay Wali Village, Balochistan
Ready for Streamlit Cloud
"""

import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
import re

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Hayyat Clinic | Dr. Rasheed Ahmad",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
def inject_css(theme="light"):
    if theme == "dark":
        bg = "#0f172a"
        card = "#1e293b"
        text = "#f1f5f9"
        muted = "#94a3b8"
        accent = "#38bdf8"
        hero = "linear-gradient(135deg, #1e3a5f 0%, #166534 50%, #854d0e 100%)"
        input_bg = "#0f172a"
        border = "#334155"
    elif theme == "eyesaver":
        bg = "#fefce8"
        card = "#fef9c3"
        text = "#422006"
        muted = "#a16207"
        accent = "#ca8a04"
        hero = "linear-gradient(135deg, #ca8a04 0%, #65a30d 50%, #0d9488 100%)"
        input_bg = "#fef9c3"
        border = "#fde68a"
    else:  # light - bright & impressive
        bg = "#f0f9ff"
        card = "#ffffff"
        text = "#0f172a"
        muted = "#64748b"
        accent = "#0ea5e9"
        hero = "linear-gradient(135deg, #0ea5e9 0%, #22c55e 50%, #eab308 100%)"
        input_bg = "#f8fafc"
        border = "#e2e8f0"

    st.markdown(f"""
    <style>
    /* Main background */
    .stApp {{
        background: {bg};
        color: {text};
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {card};
        border-right: 1px solid {border};
    }}
    
    /* Cards */
    .clinic-card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    }}
    
    /* Hero */
    .hero-box {{
        background: {hero};
        color: white;
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.25);
    }}
    .hero-box h1 {{
        font-size: 2.4rem;
        margin-bottom: 0.3rem;
        font-weight: 900;
    }}
    .hero-box p {{
        font-size: 1.15rem;
        opacity: 0.95;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        background: rgba(255,255,255,0.25);
        padding: 0.4rem 1rem;
        border-radius: 999px;
        margin: 0.3rem;
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid rgba(255,255,255,0.3);
    }}
    
    /* Availability banner */
    .avail-banner {{
        background: #22c55e;
        color: white;
        text-align: center;
        padding: 0.6rem;
        font-weight: 700;
        border-radius: 10px;
        margin-bottom: 1.2rem;
    }}
    
    /* Buttons override */
    .stButton > button {{
        border-radius: 999px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
    }}
    
    /* Doctor avatar */
    .doctor-avatar {{
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0ea5e9, #22c55e);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        color: white;
        margin: 0 auto 1rem auto;
        border: 5px solid {card};
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }}
    
    /* Payment pills */
    .pay-pill {{
        display: inline-block;
        background: {card};
        border: 1px solid {border};
        padding: 0.7rem 1.2rem;
        border-radius: 12px;
        margin: 0.3rem;
        font-weight: 600;
    }}
    
    /* Hide Streamlit branding a bit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    h1, h2, h3 {{
        color: {text} !important;
    }}
    
    p, label, .stMarkdown {{
        color: {text};
    }}
    </style>
    """, unsafe_allow_html=True)


# ==================== HELPERS ====================
def clean_phone(phone: str) -> str:
    phone = re.sub(r"\D", "", phone)
    if phone.startswith("92"):
        phone = "0" + phone[2:]
    if phone.startswith("3") and len(phone) == 10:
        phone = "0" + phone
    return phone

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


# ==================== SESSION STATE INIT ====================
if "users" not in st.session_state:
    st.session_state.users = {}          # phone -> {name, password_hash, verified}
if "otps" not in st.session_state:
    st.session_state.otps = {}           # phone -> {otp, expires}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "appointments" not in st.session_state:
    st.session_state.appointments = []


# ==================== THEME SELECTOR ====================
inject_css(st.session_state.theme)


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🏥 Hayyat Clinic")
    st.caption("Dr. Rasheed Ahmad")
    st.markdown("---")

    # Theme switcher
    theme_choice = st.radio(
        "Theme / Mode",
        options=["☀️ Light (Bright)", "🌙 Dark", "👁️ Eye Saver"],
        index=["light", "dark", "eyesaver"].index(st.session_state.theme),
        key="theme_radio"
    )
    new_theme = {"☀️ Light (Bright)": "light", "🌙 Dark": "dark", "👁️ Eye Saver": "eyesaver"}[theme_choice]
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

    if st.session_state.logged_in:
        st.success(f"Logged in as **{st.session_state.user_name}**")
        pages = ["Home", "About Doctor", "Services", "Book Appointment", "Contact", "Logout"]
    else:
        pages = ["Sign Up", "Login"]

    selected = st.radio("Navigation", pages, key="nav")
    if selected != st.session_state.page:
        st.session_state.page = selected
        if selected == "Logout":
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_phone = ""
            st.session_state.page = "Login"
        st.rerun()

    st.markdown("---")
    st.markdown("**📞 Call:** 0341-858874")
    st.markdown("**💬 WhatsApp:** 0341-6995056")
    st.markdown("🟢 **Available 24 Hours**")


# ==================== MAIN CONTENT ====================

# ---------- SIGN UP ----------
if st.session_state.page == "Sign Up":
    st.markdown('<div class="avail-banner">🟢 Doctor Available 24 Hours • Mithay Wali & Nearby Villages</div>', unsafe_allow_html=True)
    
    st.markdown("## Create Account")
    st.info("Sign up with your mobile number. You will receive an OTP to verify.")

    with st.form("signup_form"):
        name = st.text_input("Your Full Name *", placeholder="e.g. Ali Khan")
        phone = st.text_input("Mobile Number *", placeholder="03XXXXXXXXX")
        password = st.text_input("Password *", type="password", placeholder="At least 6 characters")
        submitted = st.form_submit_button("Send OTP & Continue", use_container_width=True)

        if submitted:
            phone = clean_phone(phone)
            if not name or len(name) < 2:
                st.error("Please enter a valid name.")
            elif not re.match(r"^03\d{9}$", phone):
                st.error("Please enter a valid Pakistani mobile number (03XXXXXXXXX).")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif phone in st.session_state.users and st.session_state.users[phone].get("verified"):
                st.warning("This number is already registered. Please Login.")
            else:
                otp = generate_otp()
                expires = datetime.utcnow() + timedelta(minutes=10)
                st.session_state.otps[phone] = {"otp": otp, "expires": expires}
                st.session_state.users[phone] = {
                    "name": name,
                    "password_hash": hash_password(password),
                    "verified": False
                }
                st.session_state.pending_phone = phone
                st.session_state.demo_otp = otp
                st.session_state.page = "Verify OTP"
                st.rerun()

# ---------- VERIFY OTP ----------
elif st.session_state.page == "Verify OTP":
    phone = st.session_state.get("pending_phone", "")
    st.markdown("## Enter OTP")
    st.write(f"We sent a 6-digit code to **{phone}**")

    if "demo_otp" in st.session_state:
        st.success(f"**Demo Mode OTP:** `{st.session_state.demo_otp}`")

    with st.form("otp_form"):
        user_otp = st.text_input("OTP Code *", max_chars=6, placeholder="Enter 6-digit OTP")
        submitted = st.form_submit_button("Verify & Enter Clinic", use_container_width=True)

        if submitted:
            record = st.session_state.otps.get(phone)
            if not record:
                st.error("No OTP found. Please sign up again.")
            elif datetime.utcnow() > record["expires"]:
                st.error("OTP expired. Please sign up again.")
            elif user_otp != record["otp"]:
                st.error("Incorrect OTP. Try again.")
            else:
                st.session_state.users[phone]["verified"] = True
                st.session_state.logged_in = True
                st.session_state.user_name = st.session_state.users[phone]["name"]
                st.session_state.user_phone = phone
                st.session_state.page = "Home"
                st.success("Account verified! Welcome to Hayyat Clinic.")
                st.rerun()

# ---------- LOGIN ----------
elif st.session_state.page == "Login":
    st.markdown('<div class="avail-banner">🟢 Doctor Available 24 Hours • Mithay Wali & Nearby Villages</div>', unsafe_allow_html=True)
    
    st.markdown("## Welcome Back")
    st.write("Login to book appointment at Hayyat Clinic")

    with st.form("login_form"):
        phone = st.text_input("Mobile Number *", placeholder="03XXXXXXXXX")
        password = st.text_input("Password *", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            phone = clean_phone(phone)
            user = st.session_state.users.get(phone)
            if not user or user["password_hash"] != hash_password(password):
                st.error("Invalid phone or password.")
            elif not user.get("verified"):
                st.warning("Please verify your OTP first.")
                st.session_state.pending_phone = phone
                st.session_state.page = "Verify OTP"
                st.rerun()
            else:
                st.session_state.logged_in = True
                st.session_state.user_name = user["name"]
                st.session_state.user_phone = phone
                st.session_state.page = "Home"
                st.success(f"Welcome back, {user['name']}!")
                st.rerun()

# ---------- HOME ----------
elif st.session_state.page == "Home" and st.session_state.logged_in:
    st.markdown("""
    <div class="hero-box">
        <h1>🏥 Hayyat Clinic</h1>
        <p>Quality Healthcare for Everyone</p>
        <p>📍 Mithay Wali Village & All Nearby Villages, Balochistan</p>
        <br>
        <span class="badge">🟢 Available 24 Hours</span>
        <span class="badge">👨‍⚕️ Dr. Rasheed Ahmad</span>
        <span class="badge">🏘️ Serving Local Villages</span>
        <span class="badge">🏙️ Also for City Patients</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="doctor-avatar">👨‍⚕️</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("### Dr. Rasheed Ahmad")
        st.markdown("**Village Doctor • Hayyat Clinic**")
        st.write("Dr. Rasheed Ahmad is the dedicated doctor serving **Mithay Wali** and all nearby small villages. He is available **every time** — day or night — to help patients from the village and also people coming from cities.")
        st.markdown("📞 **Call:** [0341-858874](tel:0341858874)  |  💬 **WhatsApp:** [0341-6995056](https://wa.me/923416995056)")

    st.markdown("---")
    st.markdown("### Why Choose Hayyat Clinic?")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="clinic-card"><h4>🕐 Always Available</h4><p>Doctor is available 24 hours a day, every day.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="clinic-card"><h4>🏘️ Local Village Care</h4><p>Serving Mithay Wali and all small villages around.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="clinic-card"><h4>🏙️ City Patients Welcome</h4><p>People from cities can also take appointment.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="clinic-card"><h4>💳 Easy Payments</h4><p>Cash, EasyPaisa, JazzCash, Bank/Credit Card.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="clinic-card"><h4>📱 Simple Booking</h4><p>Book appointment from your phone in a few taps.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="clinic-card"><h4>❤️ Patient First</h4><p>Friendly care for children, elders, men and women.</p></div>', unsafe_allow_html=True)

    st.markdown("### Payment Options")
    st.markdown("""
    <span class="pay-pill">💵 Cash</span>
    <span class="pay-pill">📱 EasyPaisa</span>
    <span class="pay-pill">📱 JazzCash</span>
    <span class="pay-pill">💳 Bank Card</span>
    <span class="pay-pill">💳 Credit Card</span>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("📅 Book Appointment Now", use_container_width=True, type="primary"):
        st.session_state.page = "Book Appointment"
        st.rerun()

# ---------- ABOUT ----------
elif st.session_state.page == "About Doctor" and st.session_state.logged_in:
    st.markdown("## About Dr. Rasheed Ahmad")
    st.markdown('<div class="doctor-avatar">👨‍⚕️</div>', unsafe_allow_html=True)
    st.markdown("### Dr. Rasheed Ahmad")
    st.markdown("**Hayyat Clinic • Mithay Wali, Balochistan**")
    st.write("""
    Dr. Rasheed Ahmad is the only doctor serving the village of **Mithay Wali**
    and all the small villages around it. He is committed to providing healthcare to every person
    in the area — whether they live in the village or come from the city for advice and treatment.
    
    The clinic is open and the doctor is **available at every time** (24 hours).
    Patients can walk in, call, or book an appointment online. He treats people with care,
    respect and simple language so that everyone can understand and feel comfortable.
    """)
    st.markdown("""
    **Location:** Mithay Wali Village, Balochistan  
    **Phone:** [0341-858874](tel:0341858874)  
    **WhatsApp:** [0341-6995056](https://wa.me/923416995056)
    """)

# ---------- SERVICES ----------
elif st.session_state.page == "Services" and st.session_state.logged_in:
    st.markdown("## Our Services")
    st.write("General medical care for the whole community")

    services = [
        ("🩺", "General Check-up", "Complete examination, blood pressure, basic health advice for all ages."),
        ("🤒", "Fever & Common Illness", "Treatment for fever, cold, cough, stomach problems and everyday sickness."),
        ("💊", "Medicine & Prescription", "Proper medicines and clear instructions so patients can take them correctly."),
        ("👶", "Child Care", "Care for children — fever, vaccination advice, growth related concerns."),
        ("👴", "Elderly Care", "Special attention for older patients with chronic conditions and regular check-ups."),
        ("💬", "Health Advice", "Guidance on diet, hygiene, when to visit hospital, and preventive care."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(services):
        with cols[i % 3]:
            st.markdown(f'<div class="clinic-card"><h4>{icon} {title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

    if st.button("Book Appointment for Any Service", use_container_width=True, type="primary"):
        st.session_state.page = "Book Appointment"
        st.rerun()

# ---------- APPOINTMENT ----------
elif st.session_state.page == "Book Appointment" and st.session_state.logged_in:
    st.markdown("## Book Appointment")
    st.write("Dr. Rasheed Ahmad is available 24 hours. Fill the form and we will contact you.")

    with st.form("appointment_form"):
        patient_name = st.text_input("Patient Name *", value=st.session_state.user_name)
        phone = st.text_input("Contact Number *", value=st.session_state.user_phone)
        reason = st.text_area("Reason / Problem (optional)", placeholder="Briefly describe the problem...")
        preferred_date = st.date_input("Preferred Date (optional)", value=None)
        preferred_time = st.selectbox("Preferred Time (optional)", 
                                      ["Any time (Doctor is always available)", "Morning", "Afternoon", "Evening", "Night"])
        submitted = st.form_submit_button("Submit Appointment Request", use_container_width=True)

        if submitted:
            if not patient_name or not phone:
                st.error("Name and phone are required.")
            else:
                st.session_state.appointments.append({
                    "name": patient_name,
                    "phone": phone,
                    "reason": reason,
                    "date": str(preferred_date) if preferred_date else "",
                    "time": preferred_time,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("Appointment request submitted successfully! Doctor will contact you soon.")
                st.balloons()

    st.markdown("---")
    st.markdown("Or call / WhatsApp directly: **0341-858874** / **0341-6995056**")

# ---------- CONTACT ----------
elif st.session_state.page == "Contact" and st.session_state.logged_in:
    st.markdown("## Contact Hayyat Clinic")
    st.write("We are here for you anytime")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="clinic-card" style="text-align:center;"><h3>📞</h3><h4>Call Doctor</h4><p style="font-size:1.3rem;font-weight:700;"><a href="tel:0341858874">0341-858874</a></p><p>Available 24 hours</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="clinic-card" style="text-align:center;"><h3>💬</h3><h4>WhatsApp</h4><p style="font-size:1.3rem;font-weight:700;"><a href="https://wa.me/923416995056" target="_blank">0341-6995056</a></p><p>Message anytime</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="clinic-card" style="text-align:center;"><h3>📍</h3><h4>Location</h4><p><strong>Mithay Wali Village</strong></p><p>Balochistan • Nearby villages</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.link_button("💬 Open WhatsApp Chat", "https://wa.me/923416995056?text=Assalam%20o%20Alaikum%20Doctor%2C%20I%20need%20appointment", use_container_width=True)

# ---------- FALLBACK ----------
else:
    st.session_state.page = "Login"
    st.rerun()
