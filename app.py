import streamlit as st
import pandas as pd
from fpdf import FPDF
import hashlib
import time

# Page Configuration (Sabse upar hona chahiye)
st.set_page_config(page_title="Vyapar FinPortal", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# --- Security Functions (Password Hashing) ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- Calculator Core Functions ---
def calculate_pmt(rate_per_period, number_of_periods, present_value):
    if rate_per_period == 0:
        return present_value / number_of_periods if number_of_periods else 0
    return (present_value * rate_per_period * (1 + rate_per_period)**number_of_periods) / ((1 + rate_per_period)**number_of_periods - 1)

def create_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    col_widths = [15, 35, 35, 35, 35, 35]
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, str(col), border=1, align='C')
    pdf.ln()
    pdf.set_font("Arial", '', 9)
    for index, row in df.iterrows():
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 10, str(val), border=1, align='C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

def generate_flat_schedule(principal, total_interest, periods):
    if periods <= 0: return pd.DataFrame()
    periods = int(round(periods))
    if periods == 0: periods = 1
    prin_per = principal / periods
    int_per = total_interest / periods
    emi_per = prin_per + int_per
    data = []
    out_prin = principal
    for i in range(1, periods + 1):
        closing_bal = max(0, out_prin - prin_per)
        data.append({
            "Inst.": i, "Opening Bal (₹)": f"{out_prin:.2f}", "Principal (₹)": f"{prin_per:.2f}",
            "Interest (₹)": f"{int_per:.2f}", "EMI (₹)": f"{emi_per:.2f}", "Closing Bal (₹)": f"{closing_bal:.2f}"
        })
        out_prin = closing_bal
    return pd.DataFrame(data)

def generate_red_schedule(principal, rate_per_period, emi, periods):
    if periods <= 0: return pd.DataFrame()
    periods = int(round(periods))
    if periods == 0: periods = 1
    data = []
    out_prin = principal
    for i in range(1, periods + 1):
        interest = out_prin * rate_per_period
        prin = emi - interest
        closing_bal = max(0, out_prin - prin)
        data.append({
            "Inst.": i, "Opening Bal (₹)": f"{out_prin:.2f}", "Principal (₹)": f"{prin:.2f}",
            "Interest (₹)": f"{interest:.2f}", "EMI (₹)": f"{emi:.2f}", "Closing Bal (₹)": f"{closing_bal:.2f}"
        })
        out_prin = closing_bal
    return pd.DataFrame(data)

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': make_hashes('admin123')} # Default User

# ==========================================
# AUTHENTICATION FLOW (SPLIT SCREEN UI)
# ==========================================
if not st.session_state['logged_in']:
    # Hide sidebar during login
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    </style>
    """, unsafe_allow_html=True)
    
    # Standard Columns (Removed 'gap' parameter to prevent older version TypeError)
    col_img, col_form = st.columns([1.2, 1])
    
    with col_img:
        # Left Side: Business/Finance Image (using use_column_width for stability)
        st.image("https://images.unsplash.com/photo-1554224155-6726b3ff858f?q=80&w=1000&auto=format&fit=crop", use_column_width=True)
        st.markdown("<h3 style='color: #1e3a8a;'>Empowering Your Financial Decisions</h3>", unsafe_allow_html=True)
        st.write("Advanced loan calculation and scheduling tools built for finance professionals and businesses.")

    with col_form:
        # Right Side: Clean Login/Signup Form
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>💼 Vyapar FinPortal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 20px;'>Secure Access</p>", unsafe_allow_html=True)
        
        # Radio button UI prevents 'st.tabs' TypeErrors on older versions
        action = st.radio("Choose Action:", ["Login", "Sign Up"], horizontal=True)
        
        if action == "Login":
            username = st.text_input("User ID", key="l_user")
            password = st.text_input("Password", type='password', key="l_pass")
            if st.button("Login ➔"):
                if username in st.session_state['users_db'] and check_hashes(password, st.session_state['users_db'][username]):
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = username
                    st.rerun()
                else:
                    st.error("Incorrect User ID or Password. Try again.")
                    
        elif action == "Sign Up":
            new_user = st.text_input("New User ID", key="s_user")
            new_password = st.text_input("New Password", type='password', key="s_pass")
            if st.button("Create Account & Login ➔"):
                if new_user in st.session_state['users_db']:
                    st.warning("User ID already exists! Please select Login.")
                elif len(new_user) == 0 or len(new_password) == 0:
                    st.error("Please fill all details.")
                else:
                    # Save user and auto-login
                    st.session_state['users_db'][new_user] = make_hashes(new_
