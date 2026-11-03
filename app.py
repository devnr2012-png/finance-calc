import streamlit as st
import pandas as pd
from fpdf import FPDF
import hashlib

# Page Configuration (Sabse upar hona chahiye)
st.set_page_config(page_title="Vyapar FinPortal", page_icon="💼", layout="wide")

# --- Security Functions (Password Hashing) ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- UI & Background Styling ---
def set_background():
    # Finance/Math/Vyapar theme background image
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1554224155-6726b3ff858f?q=80&w=2000&auto=format&fit=crop");
            background-attachment: fixed;
            background-size: cover;
        }
        /* Calculator section ko thoda white & transparent banane ke liye taaki text dikhe */
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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
    # Default Admin ID and Password
    st.session_state['users_db'] = {'admin': make_hashes('admin123')}

# Set Background globally
set_background()

# ==========================================
# AUTHENTICATION FLOW (LOGIN / SIGN UP)
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>💼 Vyapar FinPortal</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #475569;'>Secure Access for Finance Professionals</h4>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        menu = ["Login", "Sign Up"]
        choice = st.selectbox("Select Action", menu)
        
        if choice == "Login":
            st.subheader("Login to your account")
            username = st.text_input("User ID")
            password = st.text_input("Password", type='password')
            if st.button("Login ➔", use_container_width=True):
                if username in st.session_state['users_db'] and check_hashes(password, st.session_state['users_db'][username]):
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = username
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Incorrect User ID or Password. Try again.")
                    
        elif choice == "Sign Up":
            st.subheader("Create New Account")
            new_user = st.text_input("New User ID")
            new_password = st.text_input("New Password", type='password')
            if st.button("Create Account ➔", use_container_width=True):
                if new_user in st.session_state['users_db']:
                    st.warning("User ID already exists! Please Login.")
                elif len(new_user) == 0 or len(new_password) == 0:
                    st.error("Please fill all details.")
                else:
                    st.session_state['users_db'][new_user] = make_hashes(new_password)
                    st.success("Account created successfully! Please select 'Login' from the menu.")

# ==========================================
# MAIN DASHBOARD (Visible only after Login)
# ==========================================
else:
    # --- Sidebar ---
    st.sidebar.title(f"👤 Hi, {st.session_state['current_user']}")
    if st.sidebar.button("Logout 🚪"):
        st.session_state['logged_in'] = False
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.header("Loan Parameters")

    loan_amount = st.sidebar.number_input("Loan Amount (Principal) ₹", min_value=0.0, value=10000.0, step=1000.0)

    tenure_unit = st.sidebar.selectbox("Tenure Unit", ["Days", "Months", "Years"], index=1)
    if tenure_unit == "Days":
        tenure_value = st.sidebar.number_input("Tenure (in Days)", min_value=1.0, value=90.0, step=1.0)
        days = tenure_value
        months = tenure_value / 30
        years = tenure_value / 365
    elif tenure_unit == "Months":
        tenure_value = st.sidebar.number_input("Tenure (in Months)", min_value=1.0, value=3.0, step=1.0)
        days = tenure_value * 30
        months = tenure_value
        years = tenure_value / 12
    else:
        tenure_value = st.sidebar.number_input("Tenure (in Years)", min_value=0.1, value=1.0, step=0.5)
        days = tenure_value * 365
        months = tenure_value * 12
        years = tenure_value

    weeks = days / 7
    pf_rate = st.sidebar.number_input("Processing Fee (%)", min_value=0.0, value=1.0, step=0.1)

    st.sidebar.markdown("---")
    st.sidebar.header("Calculation Modes Setup")
    flat_rate_pa = st.sidebar.number_input("Flat Interest Rate (% P.A.)", min_value=0.0, value=12.0, step=1.0)
    red_rate_pa = st.sidebar.number_input("Reducing Interest Rate (% P.A.)", min_value=0.0, value=13.0, step=1.0)

    # --- Main Calculator UI ---
    st.title("Advanced Loan Calculator Dashboard")
    st.markdown("Analyze loan structures with Flat vs. Reducing balance comparisons.")

    pf_amount = (loan_amount * pf_rate) / 100
    disbursed_amount = loan_amount - pf_amount

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Processing Fees Deduction", value=f"₹{pf_amount:,.0f}", delta=f"{pf_rate}%", delta_color="inverse")
    with col2:
        st.metric(label="Actual Disbursed Amount", value=f"₹{disbursed_amount:,.0f}")

    st.markdown("---")

    flat_interest = flat_return = flat_daily = flat_weekly = flat_monthly = 0
    emi_monthly = emi_weekly = emi_daily = total_repayment_red = total_interest_red = 0
    monthly_rate = weekly_rate = daily_rate = 0

    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.subheader("🟧 Flat Calculation")
        flat_interest = loan_amount * (flat_rate_pa / 100) * years
        flat_return = loan_amount + flat_interest
        flat_daily = flat_return / days if days else 0
        flat_weekly = flat_return / weeks if weeks else 0
        flat_monthly = flat_return / months if months else 0

        st.metric(label="Total Expected Return", value=f"₹{flat_return:,.0f}")
        st.metric(label="Total Interest Generated", value=f"₹{flat_interest:,.0f}")
        st.info(f"**Daily EMI:** ₹{flat_daily:,.0f}\n\n**Weekly EMI:** ₹{flat_weekly:,.0f}\n\n**Monthly EMI:** ₹{flat_monthly:,.0f}")

    with res_col2:
        st.subheader("🟩 Reducing Balance")
        if red_rate_pa > 0 and days > 0:
            monthly_rate = (red_rate_pa / 12) / 100
            emi_monthly = calculate_pmt(monthly_rate, months, loan_amount)
            weekly_rate = (red_rate_pa / 52) / 100
            emi_weekly = calculate_pmt(weekly_rate, weeks, loan_amount)
            daily_rate = (red_rate_pa / 365) / 100
            emi_daily = calculate_pmt(daily_rate, days, loan_amount)
            total_repayment_red = emi_monthly * months
            total_interest_red = total_repayment_red - loan_amount

        st.metric(label="Total Repayment", value=f"₹{total_repayment_red:,.0f}")
        st.metric(label="Total Interest Generated", value=f"₹{total_interest_red:,.0f}")
        st.success(f"**Daily EMI:** ₹{emi_daily:,.0f}\n\n**Weekly EMI:** ₹{emi_weekly:,.0f}\n\n**Monthly EMI:** ₹{emi_monthly:,.0f}")

    st.markdown("---")

    # --- Schedule Generator ---
    st.subheader("📅 Repayment Schedule & Downloads")
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        sch_method = st.selectbox("Select Interest Method:", ["Flat Calculation", "Reducing Balance"])
    with sel_col2:
        sch_freq = st.selectbox("Select Repayment Frequency:", ["Daily", "Weekly", "Monthly"])

    df_schedule = pd.DataFrame()
    schedule_title = f"{sch_method} - {sch_freq} Schedule"

    if sch_method == "Flat Calculation":
        if sch_freq == "Daily": df_schedule = generate_flat_schedule(loan_amount, flat_interest, days)
        elif sch_freq == "Weekly": df_schedule = generate_flat_schedule(loan_amount, flat_interest, weeks)
        elif sch_freq == "Monthly": df_schedule = generate_flat_schedule(loan_amount, flat_interest, months)
    else:
        if sch_freq == "Daily": df_schedule = generate_red_schedule(loan_amount, daily_rate, emi_daily, days)
        elif sch_freq == "Weekly": df_schedule = generate_red_schedule(loan_amount, weekly_rate, emi_weekly, weeks)
        elif sch_freq == "Monthly": df_schedule = generate_red_schedule(loan_amount, monthly_rate, emi_monthly, months)

    if not df_schedule.empty:
        st.dataframe(df_schedule, use_container_width=True)
        
        dl_col1, dl_col2 = st.columns([1, 4])
        with dl_col1:
            try:
                pdf_bytes = create_pdf(df_schedule, schedule_title)
                st.download_button(label="📄 Download PDF", data=pdf_bytes, file_name=f"{schedule_title.replace(' ', '_')}.pdf", mime="application/pdf")
            except Exception:
                st.error("PDF module failed. Check requirements.")
        with dl_col2:
            csv = df_schedule.to_csv(index=False).encode('utf-8')
            st.download_button(label="📊 Download Excel/CSV", data=csv, file_name=f"{schedule_title.replace(' ', '_')}.csv", mime="text/csv")

    # --- Affiliate / Monetization Section ---
    st.markdown("---")
    st.subheader("🎁 Exclusive Partner Offers")
    st.write("Apply for instant loans or check your credit score for free through our trusted partners.")

    ad_col1, ad_col2, ad_col3 = st.columns(3)

    with ad_col1:
        st.info("📊 **Check Free CIBIL Score**\n\nKnow your exact credit health in 2 mins. Zero impact on score.\n\n*Powered by Experian/CIBIL*")
        st.link_button("Check Free CIBIL ➔", "https://www.paisabazaar.com/cibil-credit-report/", use_container_width=True)

    with ad_col2:
        st.success("💸 **Instant Loan up to ₹5 Lakhs**\n\n100% Paperless process. Instant approval using PAN Card.\n\n*Zero Foreclosure Charges*")
        st.link_button("Apply & Get Cash ➔", "https://kreditbee.in/", use_container_width=True)

    with ad_col3:
        st.warning("💳 **Lifetime Free Credit Card**\n\nEarn flat 5% cashback on all online spends. No joining fee.\n\n*Instant Virtual Card*")
        st.link_button("Apply for Card ➔", "https://www.sbicard.com/", use_container_width=True)

    st.caption("Disclaimer: By clicking these links, you will be redirected to our partner websites. We may earn a commission on successful disbursals.")
