import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(
    page_title="Retirement Expenditure Simulator",
    page_icon="📊",
    layout="centered"
)


st.title("Retirement Expenditure Simulator")

st.caption(
    "Inflation-adjusted retirement expenditure estimation "
    "using deterministic scenarios and Monte Carlo simulation."
)

st.divider()


# -----------------------------
# User inputs
# -----------------------------

st.subheader("Personal Details")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "Current age",
        min_value=18,
        max_value=100,
        value=25,
        step=1
    )

with col2:
    retirement_age = st.number_input(
        "Retirement age",
        min_value=18,
        max_value=100,
        value=60,
        step=1
    )

monthly_expense = st.number_input(
    "Current monthly expenditure (₹)",
    min_value=0.0,
    value=50000.0,
    step=1000.0
)


if retirement_age <= age:

    st.error("Retirement age must be greater than current age.")

else:

    years_left = retirement_age - age

    # =========================================================
    # DETERMINISTIC INFLATION SCENARIOS
    # =========================================================

    st.divider()
    st.subheader("Inflation Scenario Analysis")

    inflation_rates = [0.02, 0.03, 0.04, 0.05, 0.06]

    results = []

    for rate in inflation_rates:

        future_expense = monthly_expense * (1 + rate) ** years_left

        results.append({
            "Inflation Rate": f"{rate * 100:.0f}%",
            "Monthly Expense at Retirement": future_expense
        })


    df = pd.DataFrame(results)

    average_expense = df[
        "Monthly Expense at Retirement"
    ].mean()


    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Years to Retirement",
            f"{years_left}"
        )

    with col2:
        st.metric(
            "Average Projected Expense",
            f"₹{average_expense:,.0f} / month"
        )


    display_df = df.copy()

    display_df["Monthly Expense at Retirement"] = display_df[
        "Monthly Expense at Retirement"
    ].apply(lambda x: f"₹{x:,.0f}")


    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True
    )


st.divider()


# -----------------------------
# Stochastic inflation model
# -----------------------------
# Based on the paper:
#
# Annual inflation ~ Normal(mean = 4%, standard deviation = 1%)
#
# Mean inflation = 4%
# Inflation volatility = 1%
#
# This means each future year's inflation rate is randomly
# generated around 4%, with a standard deviation of 1 percentage point.
#
# We simulate 1,000 possible inflation paths from the user's
# current age until retirement.

mean_inflation = 0.04
inflation_volatility = 0.01
num_simulations = 1000

st.divider()
st.subheader("Monte Carlo Inflation Model")

st.caption(
        "Annual inflation is modelled as a stochastic process "
        "and simulated independently across future years."
)


# Stochastic model assumptions
#
    # Annual inflation:
    #
    # I_t ~ Normal(mean = 4%, standard deviation = 1%)
    #
    # Mean annual inflation      = 4%
    # Inflation volatility      = 1%
    # Number of simulations     = 1,000
    #
    # For every Monte Carlo simulation, a new path of annual
    # inflation rates is generated from the current age until
    # retirement.
    #
    # Monthly expenditure evolves according to:
    #
    # E_t = E_(t-1) * (1 + I_t)

mean_inflation = 0.04
inflation_volatility = 0.01
num_simulations = 1000

rng = np.random.default_rng(42)

final_expenses = []


for _ in range(num_simulations):

    yearly_inflation = rng.normal(
        loc=mean_inflation,
        scale=inflation_volatility,
        size=years_left
    )

    future_expense = monthly_expense

    for inflation in yearly_inflation:
        future_expense *= (1 + inflation)

    final_expenses.append(future_expense)


expected_expense = np.mean(final_expenses)

lower_bound = np.percentile(
    final_expenses,
    5
)
    # Generate one possible path of yearly inflation rates
yearly_inflation = rng.normal(
    loc=mean_inflation,
    scale=inflation_volatility,
    size=years_left
)

upper_bound = np.percentile(
    final_expenses,
    95
)

    # Compound expenditure using the simulated inflation path
for inflation in yearly_inflation:
    future_expense *= (1 + inflation)

    # -----------------------------
    # Model parameters
    # -----------------------------

st.write("##### Model Parameters")

col1, col2, col3 = st.columns(3)
# Monte Carlo results
expected_expense = np.mean(final_expenses)
lower_bound = np.percentile(final_expenses, 5)
upper_bound = np.percentile(final_expenses, 95)

with col1:
    st.metric(
        "Mean Inflation",
        "4.0%"
    )

with col2:
    st.metric(
        "Inflation Volatility",
        "1.0%"
    )

with col3:
    st.metric(
        "Simulations",
        f"{num_simulations:,}"
    )


    # -----------------------------
    # Monte Carlo results
    # -----------------------------

st.write("##### Simulation Results")

st.metric(
    "Expected Monthly Expenditure at Retirement",
    f"₹{expected_expense:,.0f}"
)


st.info(
    f"90% simulated interval: "
    f"₹{lower_bound:,.0f} – ₹{upper_bound:,.0f} per month"
)


st.divider()
# Show model assumptions
st.write("**Model assumptions**")
st.write(f"Mean annual inflation: **{mean_inflation * 100:.0f}%**")
st.write(
    f"Annual inflation volatility: "
    f"**{inflation_volatility * 100:.0f}%**"
)
st.write(f"Monte Carlo simulations: **{num_simulations:,}**")


# Show results
st.metric(
    "Expected monthly expenditure",
    f"₹{expected_expense:,.0f}"
)

st.caption(
    "Estimates are based on assumed inflation dynamics and are "
    "intended for analytical purposes."
)

    
