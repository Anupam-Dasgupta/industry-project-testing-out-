import streamlit as st
import pandas as pd
import numpy as np


st.title("Retirement Expense Calculator")

st.write(
    "Estimate your monthly expenditure at retirement "
    "under different inflation assumptions."
)


age = st.number_input(
    "Current age",
    min_value=18,
    max_value=100,
    value=25,
    step=1
)

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
    st.error("Retirement age must be greater than your current age.")

else:
    years_left = retirement_age - age

    inflation_rates = [0.02, 0.03, 0.04, 0.05, 0.06]

    results = []

    for rate in inflation_rates:
        future_expense = monthly_expense * (1 + rate) ** years_left

        results.append({
            "Inflation Rate": f"{rate * 100:.0f}%",
            "Monthly Expense at Retirement": future_expense
        })

    df = pd.DataFrame(results)

    average_expense = df["Monthly Expense at Retirement"].mean()

    st.divider()

    st.subheader("Estimated Monthly Expense at Retirement")

    st.metric(
        "Average across inflation scenarios",
        f"₹{average_expense:,.0f}"
    )

    st.write(f"Years until retirement: **{years_left} years**")

    display_df = df.copy()

    display_df["Monthly Expense at Retirement"] = display_df[
        "Monthly Expense at Retirement"
    ].apply(lambda x: f"₹{x:,.0f}")

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True
    )

import numpy as np

st.divider()

st.subheader("Stochastic Inflation Estimate")

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

rng = np.random.default_rng(42)

final_expenses = []

for _ in range(num_simulations):

    # Generate one possible path of yearly inflation rates
    yearly_inflation = rng.normal(
        loc=mean_inflation,
        scale=inflation_volatility,
        size=years_left
    )

    future_expense = monthly_expense

    # Compound expenditure using the simulated inflation path
    for inflation in yearly_inflation:
        future_expense *= (1 + inflation)

    final_expenses.append(future_expense)


# Monte Carlo results
expected_expense = np.mean(final_expenses)
lower_bound = np.percentile(final_expenses, 5)
upper_bound = np.percentile(final_expenses, 95)


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

st.write(
    f"90% of simulated outcomes fall approximately between "
    f"**₹{lower_bound:,.0f}** and **₹{upper_bound:,.0f}** per month."
)

    
