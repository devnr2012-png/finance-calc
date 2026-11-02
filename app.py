import streamlit as st
import pandas as pd
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="FinPortal Calculator", page_icon="💼", layout="wide")

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
    
    # Table Header
    pdf.set_font("Arial", 'B', 9)
    col_widths = [15, 35, 35, 35, 35, 35]
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, str(col), border=1, align='C')
    pdf.ln()
    
    # Table Data
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
            "Inst.": i,
            "Opening Bal (₹)": f"{out_prin:.2f}",
            "Principal (₹)": f"{prin_per:.2f}",
            "Interest (₹)": f"{int_per:.2f}",
            "EMI (₹)": f"{emi_per:.2f}",
            "Closing Bal (₹)": f"{closing_bal:.2f}"
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
            "Inst.": i,
            "Opening Bal (₹)": f"{out_prin:.2f}",
            "Principal (₹)": f"{prin:.2f}",
            "Interest (₹)": f"{interest:.2f}",
            "EMI (₹)": f"{emi:.2f}",
            "Closing Bal (₹)": f"{closing_bal:.2f}"
        })
        out_prin = closing_bal
    return pd.DataFrame(data)


# --- Sidebar Inputs ---
st.sidebar.title("💼 FinPortal")
st.sidebar.markdown("---")
st.sidebar.header("Loan Parameters")

loan_amount = st.sidebar.number_input("Loan Amount (Principal) ₹", min_value=0.0, value=10000.0, step=1000.0)

# Tenure Setup
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


# --- Main Dashboard ---
st.title("Advanced Loan Calculator Dashboard")
st.markdown("Analyze loan structures with Flat vs. Reducing balance comparisons.")

# Initial Deductions
pf_amount = (loan_amount * pf_rate)
