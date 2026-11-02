import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# Page Configuration
st.set_page_config(page_title="FinPortal Calculator", page_icon="💼", layout="wide")

def calculate_pmt(rate_per_period, number_of_periods, present_value):
    if rate_per_period == 0:
        return present_value / number_of_periods if number_of_periods else 0
    return (present_value * rate_per_period * (1 + rate_per_period)**number_of_periods) / ((1 + rate_per_period)**number_of_periods - 1)

def create_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    col_widths = [15, 35, 35, 35, 35, 35]
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, col, border=1, align='C')
    pdf.ln()
    
    # Table Data
    pdf.set_font("Arial", '', 10)
    for index, row in df.iterrows():
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 10, str(val), border=1, align='C')
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# --- Sidebar Inputs ---
st.sidebar.title("💼 FinPortal")
st.sidebar.markdown("---")
st.sidebar.header("Loan Parameters")

loan_amount = st.sidebar.number_input("Loan Amount (Principal) ₹", min_value=0, value=10000, step=1000)

# Tenure Setup (Days, Months, Years)
tenure_unit = st.sidebar.selectbox("Tenure Unit", ["Days", "Months", "Years"], index=1)
if tenure_unit == "Days":
    tenure_value = st.sidebar.number_input("Tenure (in Days)", min_value=1, value=90, step=1)
    days = tenure_value
    months = tenure_value / 30
    years = tenure_value / 365
elif tenure_unit == "Months":
    tenure_value = st.sidebar.number_input("Tenure (in Months)", min_value=1, value=3, step=1)
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
red_rate_pa = st.sidebar.number_input("Reducing Interest Rate (% P.A.)", min_value=0.0, value=21.0, step=1.0)
flat_rate_pa = st.sidebar.number_input("Flat Interest Rate (% P.A.)", min_value=0.0, value=10.0, step=1.0)


# --- Main Dashboard ---
st.title("Advanced Loan Calculator Dashboard")
st.markdown("Analyze loan structures with Flat vs. Reducing balance comparisons.")

# Initial Deductions Calculation
pf_amount = (loan_amount * pf_rate) / 100
disbursed_amount = loan_amount - pf_amount

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Processing Fees Deduction", value=f"₹{pf_amount:,.0f}", delta=f"{pf_rate}%", delta_color="inverse")
with col2:
    st.metric(label="Actual Disbursed Amount", value=f"₹{disbursed_amount:,.0f}")

st.markdown("---")

# Display Results
res_col1, res_col2 = st.columns(2)

# --- FLAT CALCULATION ---
with res_col1:
    st.subheader("🟧 Flat Calculation")
    
    flat_interest = loan_amount * (flat_rate_pa / 100) * years
    flat_return = loan_amount + flat_interest
    
    flat_daily = flat_return / days if days else 0
    flat_weekly = flat_return / weeks if weeks else 0
    flat_monthly = flat_return / months if months else 0

    st.metric(label="Total Expected Return", value=f"₹{flat_return:,.0f}")
    st.metric(label="Total Interest Generated", value=f"₹{flat_interest:,.0f}")
    
    st.markdown("#### EMI Breakdown")
    st.info(f"**Daily EMI:** ₹{flat_daily:,.0f}")
    st.info(f"**Weekly EMI:** ₹{flat_weekly:,.0f}")
    st.info(f"**Monthly EMI:** ₹{flat_monthly:,.0f}")


# --- REDUCING CALCULATION ---
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
    else:
        total_repayment_red = total_interest_red = emi_monthly = emi_weekly = emi_daily = 0

    st.metric(label="Total Repayment", value=f"₹{total_repayment_red:,.0f}")
    st.metric(label="Total Interest Generated", value=f"₹{total_interest_red:,.0f}")
    
    st.markdown("#### EMI Breakdown")
    st.success(f"**Daily EMI:** ₹{emi_daily:,.0f}")
    st.success(f"**Weekly EMI:** ₹{emi_weekly:,.0f}")
    st.success(f"**Monthly EMI:** ₹{emi_monthly:,.0f}")

st.markdown("---")

# --- REPAYMENT SCHEDULE ---
st.subheader("📅 Monthly Repayment Schedule (Reducing Balance)")

schedule_data = []
out_prin = loan_amount
for i in range(1, int(max(1, round(months))) + 1):
    interest = out_prin * monthly_rate
    prin = emi_monthly - interest
    closing_bal = max(0, out_prin - prin)
    
    schedule_data.append({
        "Inst.": i,
        "Opening Bal (₹)": f"{out_prin:.2f}",
        "Principal (₹)": f"{prin:.2f}",
        "Interest (₹)": f"{interest:.2f}",
        "EMI (₹)": f"{emi_monthly:.2f}",
        "Closing Bal (₹)": f"{closing_bal:.2f}"
    })
    out_prin -= prin

df_schedule = pd.DataFrame(schedule_data)
st.dataframe(df_schedule, use_container_width=True)

# Export Options
col_dl1, col_dl2 = st.columns([1, 4])

with col_dl1:
    # PDF Download Button
    try:
        pdf_bytes = create_pdf(df_schedule, "Monthly Repayment Schedule (Reducing Balance)")
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name="Repayment_Schedule.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error("PDF generation failed. Please ensure 'fpdf' is installed.")

with col_dl2:
    # CSV Download Button (Fallback)
    csv = df_schedule.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Download Excel/CSV",
        data=csv,
        file_name="Repayment_Schedule.csv",
        mime="text/csv",
    )
