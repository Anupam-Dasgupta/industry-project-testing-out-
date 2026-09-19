import streamlit as st
import pandas as pd


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
