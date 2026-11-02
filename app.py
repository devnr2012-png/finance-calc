import streamlit as st

# Page Configuration
st.set_page_config(page_title="FinPortal Calculator", page_icon="💼", layout="wide")

def calculate_pmt(rate_per_period, number_of_periods, present_value):
    if rate_per_period == 0:
        return present_value / number_of_periods if number_of_periods else 0
    return (present_value * rate_per_period * (1 + rate_per_period)**number_of_periods) / ((1 + rate_per_period)**number_of_periods - 1)

# Sidebar for Inputs
st.sidebar.title("💼 FinPortal")
st.sidebar.markdown("---")
st.sidebar.header("Loan Parameters")

loan_amount = st.sidebar.number_input("Loan Amount (Principal) ₹", min_value=0, value=10000, step=1000)
tenure_days = st.sidebar.number_input("Tenure (in Days)", min_value=1, value=90, step=1)
pf_rate = st.sidebar.number_input("Processing Fee (%)", min_value=0.0, value=1.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("Calculation Modes Setup")
flat_return = st.sidebar.number_input("Flat Expected Return ₹", min_value=0, value=13000, step=500)
red_rate_pa = st.sidebar.number_input("Reducing Interest Rate (% P.A.)", min_value=0.0, value=36.0, step=1.0)

# Main Dashboard
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

# Time conversions
months = tenure_days / 30
weeks = tenure_days / 7

# Display Results
res_col1, res_col2 = st.columns(2)

# FLAT CALCULATION
with res_col1:
    st.subheader("🟧 Flat Calculation")
    
    flat_interest = flat_return - loan_amount if flat_return > loan_amount else 0
    flat_daily = flat_return / tenure_days if tenure_days else 0
    flat_weekly = flat_return / weeks if weeks else 0
    flat_monthly = flat_return / months if months else 0

    st.metric(label="Total Expected Return", value=f"₹{flat_return:,.0f}")
    st.metric(label="Total Interest Generated", value=f"₹{flat_interest:,.0f}")
    
    st.markdown("#### EMI Breakdown")
    st.info(f"**Daily EMI:** ₹{flat_daily:,.0f}")
    st.info(f"**Weekly EMI:** ₹{flat_weekly:,.0f}")
    st.info(f"**Monthly EMI:** ₹{flat_monthly:,.0f}")


# REDUCING CALCULATION
with res_col2:
    st.subheader("🟩 Reducing Balance")
    
    if red_rate_pa > 0 and tenure_days > 0:
        monthly_rate = (red_rate_pa / 12) / 100
        emi_monthly = calculate_pmt(monthly_rate, months, loan_amount)
        
        weekly_rate = (red_rate_pa / 52) / 100
        emi_weekly = calculate_pmt(weekly_rate, weeks, loan_amount)
        
        daily_rate = (red_rate_pa / 365) / 100
        emi_daily = calculate_pmt(daily_rate, tenure_days, loan_amount)

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
st.caption("Developed using Streamlit | Data is calculated in real-time based on sidebar inputs.")
