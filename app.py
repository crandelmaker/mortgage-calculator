import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import io

# Set page config
st.set_page_config(
    page_title="Mortgage Overpayment Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
    }
    .success-box {
        background-color: #ac9ed6;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🏠 Mortgage Overpayment Calculator</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #555;">
            Calculate how much time and money you can save by overpaying your mortgage
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.markdown('<h2 class="section-header">📋 Your Details</h2>', unsafe_allow_html=True)
        
        # Mortgage Details
        st.markdown("### 🏠 Mortgage Information")
        current_balance = st.number_input(
            "Current mortgage balance (£)",
            min_value=1000,
            value=100000,
            step=1000,
            help="How much do you still owe on your mortgage?"
        )
        
        original_term = st.number_input(
            "Original mortgage term (years)",
            min_value=5,
            max_value=50,
            value=25,
            step=1
        )
        
        # Fixed Rate Periods
        st.markdown("### 🔒 Fixed Rate Periods")
        
        num_periods = st.number_input("Number of fixed rate periods", min_value=1, max_value=5, value=2)
        
        fixed_periods = []
        for i in range(num_periods):
            st.markdown(f"**Period {i+1}:**")
            col1, col2 = st.columns(2)
            with col1:
                months = st.number_input(f"Length (months)", min_value=1, max_value=120, value=24 if i == 0 else 60, key=f"months_{i}")
            with col2:
                rate = st.number_input(f"Rate (%)", min_value=0.0, max_value=20.0, value=4.1 if i == 0 else 3.4, step=0.1, key=f"rate_{i}")
            fixed_periods.append((months, rate / 100))
        
        svr_rate = st.number_input(
            "Standard Variable Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            help="The rate after your fixed periods end"
        ) / 100
        
        # Income & Expenses
        st.markdown("### 💰 Income & Expenses")
        monthly_income = st.number_input(
            "Monthly net income (£)",
            min_value=1000,
            value=3130,
            step=50
        )
        
        monthly_expenses = st.number_input(
            "Monthly expenses (£)",
            min_value=500,
            value=2000,
            step=50
        )
        
        income_growth = st.number_input(
            "Annual income growth (%)",
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.1
        ) / 100
        
        expense_growth = st.number_input(
            "Annual expense growth (%)",
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.1
        ) / 100
        
        # Savings
        st.markdown("### 💳 Savings & Emergency Fund")
        current_savings = st.number_input(
            "Current savings (£)",
            min_value=0,
            value=16000,
            step=1000
        )
        
        savings_rate = st.number_input(
            "Savings interest rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=3.6,
            step=0.1
        ) / 100
        
        savings_tax = st.number_input(
            "Tax on savings interest (%)",
            min_value=0.0,
            max_value=50.0,
            value=20.0,
            step=1.0
        ) / 100
        
        emergency_months = st.number_input(
            "Emergency fund (months of income)",
            min_value=1.0,
            max_value=12.0,
            value=4.0,
            step=0.5
        )
        
        # Overpayment Strategy
        st.markdown("### 🚀 Overpayment Settings")
        min_threshold = st.number_input(
            "Minimum overpayment threshold (£)",
            min_value=500,
            value=1000,
            step=100,
            help="Minimum spare cash needed to trigger an overpayment"
        )
        
        simulation_years = st.number_input(
            "Simulation period (years)",
            min_value=5,
            max_value=50,
            value=30,
            step=1
        )
        
        # Calculate button
        if st.button("🔄 Calculate Results", type="primary"):
            st.session_state.calculate = True
    
    # Main content area
    if hasattr(st.session_state, 'calculate') and st.session_state.calculate:
        
        # Prepare data for simulation
        data = {
            'initial_mortgage': current_balance,
            'mortgage_term_years': original_term,
            'fixed_periods': fixed_periods,
            'mortgage_rate_after_fixed': svr_rate,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'income_growth_rate': income_growth,
            'expense_growth_rate': expense_growth,
            'initial_savings': current_savings,
            'savings_rate': savings_rate,
            'savings_tax_rate': savings_tax,
            'emergency_buffer': monthly_income * emergency_months,
            'min_overpayment_threshold': min_threshold,
            'total_years_to_simulate': simulation_years
        }
        
        # Run simulation
        with st.spinner("Running simulation..."):
            results = run_simulation(data)
        
        # Display results
        display_results(results, data)
    
    else:
        # Initial instructions
        st.markdown("""
        <div class="success-box">
            <h3>👈 Get Started</h3>
            <p>Fill in your mortgage details in the sidebar, then click <strong>"Calculate Results"</strong> to see:</p>
            <ul>
                <li>💰 How much interest you'll save</li>
                <li>📅 When you'll be mortgage-free</li>
                <li>📊 Interactive charts showing your progress</li>
                <li>📁 Downloadable detailed breakdown</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Example scenario
        st.markdown('<h2 class="section-header">💡 Example Scenario</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Current Balance", "£100,000")
            st.metric("📅 Original Term", "25 years")
        with col2:
            st.metric("💵 Monthly Income", "£3,130")
            st.metric("🏠 Monthly Expenses", "£2,000")
        with col3:
            st.metric("💳 Current Savings", "£16,000")
            st.metric("🛡️ Emergency Fund", "4 months")

def run_simulation(data):
    """Run the mortgage simulation"""
    # Setup variables
    months = data['total_years_to_simulate'] * 12
    mortgage_balance = data['initial_mortgage']
    monthly_savings_rate = data['savings_rate'] / 12
    cash_savings = data['initial_savings']
    monthly_income = data['monthly_income']
    monthly_expenses = data['monthly_expenses']
    
    # Setup fixed periods
    fixed_period_schedule = []
    start_month = 0
    for period_length, rate in data['fixed_periods']:
        fixed_period_schedule.append((start_month, start_month + period_length, rate))
        start_month += period_length
    
    # Calculate initial payment
    n_payments_total = data['mortgage_term_years'] * 12
    if fixed_period_schedule:
        current_rate = fixed_period_schedule[0][2]
    else:
        current_rate = data['mortgage_rate_after_fixed']
    
    standard_monthly_payment = npf.pmt(current_rate/12, n_payments_total, -data['initial_mortgage'])
    
    # Tracking lists
    mortgage_balances = []
    savings_balances = []
    total_overpayments_cumulative = []
    years = []
    monthly_incomes = []
    monthly_expenses_list = []
    overpayments = []
    available_cashes = []
    mortgage_payments = []
    overpayment_events = []
    
    # Simulation variables
    total_interest_paid = 0
    months_to_mortgage_free = None
    yearly_overpayment_limit = 0.10 * mortgage_balance
    mortgage_paid_off = False
    overpayment_made_this_year = False
    current_year = 0
    cumulative_overpayments = 0
    
    for month in range(months):
        if mortgage_paid_off:
            break
        
        lump_sum = 0
        
        if mortgage_balance <= 0:
            months_to_mortgage_free = month
            mortgage_balance = 0
            standard_monthly_payment = 0
            mortgage_paid_off = True
            break
        
        # Reset yearly overpayment allowance
        if month % 12 == 0:
            yearly_overpayment_limit = 0.10 * mortgage_balance
            overpayment_made_this_year = False
            current_year = month // 12
        
        # Apply growth rates
        if month > 0 and month % 12 == 0:
            monthly_income *= (1 + data['income_growth_rate'])
            monthly_expenses *= (1 + data['expense_growth_rate'])
        
        # Calculate available cash
        available_cash = monthly_income - monthly_expenses
        
        # Check for end of fixed period overpayments
        end_of_fixed_period = False
        for idx, (start_m, end_m, rate) in enumerate(fixed_period_schedule):
            if month == end_m:
                end_of_fixed_period = True
                lump_sum = max(0, cash_savings - data['emergency_buffer'])
                if lump_sum > 0:
                    payment_to_mortgage = min(lump_sum, mortgage_balance)
                    mortgage_balance -= payment_to_mortgage
                    cash_savings -= payment_to_mortgage
                    lump_sum = payment_to_mortgage
                    cumulative_overpayments += payment_to_mortgage
                    overpayment_events.append({
                        'month': month,
                        'amount': payment_to_mortgage,
                        'type': f'End of fixed period {idx + 1}'
                    })
                    overpayment_made_this_year = False
                
                # Update payment
                if mortgage_balance > 0:
                    remaining_term = data['mortgage_term_years'] * 12 - month
                    next_rate = next((r for s, e, r in fixed_period_schedule if s <= month < e), 
                                   data['mortgage_rate_after_fixed'])
                    standard_monthly_payment = npf.pmt(next_rate/12, remaining_term, -mortgage_balance)
                break
        
        # Variable rate period overpayments
        if not end_of_fixed_period and fixed_period_schedule:
            last_fixed_period_end = fixed_period_schedule[-1][1]
            if month > last_fixed_period_end:
                potential_lump_sum = max(0, cash_savings - data['emergency_buffer'])
                if potential_lump_sum >= data['min_overpayment_threshold']:
                    payment_to_mortgage = min(potential_lump_sum, mortgage_balance)
                    mortgage_balance -= payment_to_mortgage
                    cash_savings -= payment_to_mortgage
                    lump_sum = payment_to_mortgage
                    cumulative_overpayments += payment_to_mortgage
                    overpayment_events.append({
                        'month': month,
                        'amount': payment_to_mortgage,
                        'type': 'Variable rate period'
                    })
        
        # Regular mortgage payment
        applicable_rate = next((r for s, e, r in fixed_period_schedule if s <= month < e), 
                             data['mortgage_rate_after_fixed'])
        interest_payment = mortgage_balance * (applicable_rate / 12)
        capital_repayment = standard_monthly_payment - interest_payment
        
        mortgage_balance -= capital_repayment
        total_interest_paid += interest_payment
        available_cash -= standard_monthly_payment
        
        # Annual overpayment
        current_overpayment = 0
        if not overpayment_made_this_year and cash_savings > data['emergency_buffer']:
            spare_cash = cash_savings - data['emergency_buffer']
            if spare_cash >= data['min_overpayment_threshold']:
                potential_overpayment = min(spare_cash, yearly_overpayment_limit, mortgage_balance)
                if potential_overpayment > 0:
                    mortgage_balance -= potential_overpayment
                    cash_savings -= potential_overpayment
                    current_overpayment = potential_overpayment
                    cumulative_overpayments += potential_overpayment
                    overpayment_made_this_year = True
                    overpayment_events.append({
                        'month': month,
                        'amount': potential_overpayment,
                        'type': f'Annual overpayment (Year {current_year + 1})'
                    })
        
        # Handle savings
        if available_cash > 0:
            interest_earned = cash_savings * monthly_savings_rate * (1 - data['savings_tax_rate'])
            cash_savings += interest_earned + available_cash
        
        # Track progress
        mortgage_balances.append(mortgage_balance)
        savings_balances.append(cash_savings)
        total_overpayments_cumulative.append(cumulative_overpayments)
        years.append(month / 12)
        monthly_incomes.append(monthly_income)
        monthly_expenses_list.append(monthly_expenses)
        overpayments.append(current_overpayment + lump_sum)
        available_cashes.append(available_cash)
        mortgage_payments.append(capital_repayment + interest_payment)
    
    # Calculate interest saved
    if data['fixed_periods']:
        full_term_rate = data['fixed_periods'][0][1]
    else:
        full_term_rate = data['mortgage_rate_after_fixed']
    
    full_term_payment = npf.pmt(full_term_rate/12, data['mortgage_term_years'] * 12, -data['initial_mortgage'])
    total_full_term_interest = full_term_payment * data['mortgage_term_years'] * 12 - data['initial_mortgage']
    interest_saved = total_full_term_interest - total_interest_paid
    
    return {
        'months_to_mortgage_free': months_to_mortgage_free,
        'total_interest_paid': total_interest_paid,
        'interest_saved': interest_saved,
        'final_savings': cash_savings,
        'total_overpayments': cumulative_overpayments,
        'mortgage_balances': mortgage_balances,
        'savings_balances': savings_balances,
        'total_overpayments_cumulative': total_overpayments_cumulative,
        'years': years,
        'monthly_incomes': monthly_incomes,
        'monthly_expenses': monthly_expenses_list,
        'overpayments': overpayments,
        'available_cashes': available_cashes,
        'mortgage_payments': mortgage_payments,
        'overpayment_events': overpayment_events
    }

def display_results(results, data):
    """Display the simulation results"""
    
    st.markdown('<h2 class="section-header">📊 Your Results</h2>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if results['months_to_mortgage_free']:
            years = results['months_to_mortgage_free'] // 12
            months = results['months_to_mortgage_free'] % 12
            st.metric(
                "🎉 Mortgage-Free In",
                f"{years}y {months}m",
                delta=f"-{data['mortgage_term_years'] - years:.1f} years",
                delta_color="inverse"
            )
        else:
            st.metric("❌ Mortgage Status", "Not paid off", f"in {data['total_years_to_simulate']} years")
    
    with col2:
        st.metric(
            "💰 Interest Paid",
            f"£{results['total_interest_paid']:,.0f}",
            delta=f"-£{results['interest_saved']:,.0f} saved",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "🏦 Final Savings",
            f"£{results['final_savings']:,.0f}"
        )
    
    with col4:
        st.metric(
            "🚀 Total Overpayments",
            f"£{results['total_overpayments']:,.0f}"
        )
    
    # Overpayment events
    if results['overpayment_events']:
        st.markdown('<h3 class="section-header">🚀 Overpayment Schedule</h3>', unsafe_allow_html=True)
        events_df = pd.DataFrame(results['overpayment_events'])
        events_df['Year'] = (events_df['month'] / 12).round(1)
        events_df['Amount'] = events_df['amount'].apply(lambda x: f"£{x:,.0f}")
        
        st.dataframe(
            events_df[['Year', 'Amount', 'type']].rename(columns={'type': 'Type'}),
            use_container_width=True,
            hide_index=True
        )
    
    # Charts
    create_charts(results, data)
    
    # Export option
    st.markdown('<h3 class="section-header">📁 Export Data</h3>', unsafe_allow_html=True)
    
    # Create downloadable dataframe
    export_df = pd.DataFrame({
        'Year': results['years'],
        'Mortgage Balance': results['mortgage_balances'],
        'Savings Balance': results['savings_balances'],
        'Total Overpayments': results['total_overpayments_cumulative'],
        'Monthly Income': results['monthly_incomes'],
        'Monthly Expenses': results['monthly_expenses'],
        'Overpayment': results['overpayments'],
        'Available Cash': results['available_cashes']
    })
    
    # Convert to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, sheet_name='Mortgage Simulation', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': [
                'Original Mortgage',
                'Mortgage Term (Years)',
                'Months to Mortgage Free',
                'Total Interest Paid',
                'Interest Saved',
                'Final Savings Balance'
            ],
            'Value': [
                f"£{data['initial_mortgage']:,.0f}",
                data['mortgage_term_years'],
                results['months_to_mortgage_free'] or 'Not paid off',
                f"£{results['total_interest_paid']:,.0f}",
                f"£{results['interest_saved']:,.0f}",
                f"£{results['final_savings']:,.0f}"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    st.download_button(
        label="📊 Download Detailed Excel Report",
        data=output.getvalue(),
        file_name=f"mortgage_simulation_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def create_charts(results, data):
    """Create interactive charts"""
    
    st.markdown('<h3 class="section-header">📈 Interactive Charts</h3>', unsafe_allow_html=True)
    
    # Main balance chart
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Mortgage vs Savings Balance Over Time',
            'Monthly Overpayments',
            'Income vs Expenses Growth',
            'Available Cash After Payments'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Chart 1: Balances
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['mortgage_balances'], 
                  name='Mortgage Balance', line=dict(color='red', width=3)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['savings_balances'], 
                  name='Savings Balance', line=dict(color='green', width=3)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['total_overpayments_cumulative'], 
                  name='Total Overpayments', line=dict(color='blue', width=3, dash='dash')),
        row=1, col=1
    )
    
    # Chart 2: Overpayments
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['overpayments'], 
                  name='Overpayments', line=dict(color='purple', width=2)),
        row=1, col=2
    )
    
    # Chart 3: Income vs Expenses
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['monthly_incomes'], 
                  name='Income', line=dict(color='green', width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['monthly_expenses'], 
                  name='Expenses', line=dict(color='red', width=2)),
        row=2, col=1
    )
    
    # Chart 4: Available Cash
    fig.add_trace(
        go.Scatter(x=results['years'], y=results['available_cashes'], 
                  name='Available Cash', line=dict(color='orange', width=2)),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="Mortgage Overpayment Analysis")
    fig.update_xaxes(title_text="Years")
    fig.update_yaxes(title_text="Amount (£)")
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()