import plotly.express as px
import streamlit as st

from utils import configure_page, header, load_csv, style_figure

configure_page("Observation Trends", "📈")
header("Observation Trends", "Temporal coverage and observation-method composition.")
annual = load_csv("annual_trends.csv")
monthly = load_csv("monthly.csv")
methods = load_csv("methods.csv")
latest_year = int(annual["Observation_Year"].max())
complete = annual[annual["Observation_Year"] < latest_year]
partial = annual.loc[annual["Observation_Year"] == latest_year].iloc[0]

m1, m2, m3 = st.columns(3)
m1.metric("Complete years", f"{int(complete.Observation_Year.min())}–{latest_year - 1}")
m2.metric(f"Partial {latest_year} records", f"{partial.Observation_Count:,.0f}")
m3.metric("Monthly categories", len(monthly))

c1, c2 = st.columns(2)
with c1:
    fig = px.line(
        complete, x="Observation_Year", y="Observation_Count",
        markers=True, title="Annual records — complete years only",
        labels={"Observation_Year": "Year", "Observation_Count": "Records"},
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)
with c2:
    fig = px.bar(
        monthly, x="Observation_Month_Name", y="Observation_Count",
        title="Monthly record composition",
        labels={
            "Observation_Month_Name": "Month",
            "Observation_Count": "Records",
        },
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)

fig = px.bar(
    methods.sort_values("Observation_Count"),
    x="Observation_Count", y="Observation_Method", orientation="h",
    text="Observation_Count", title="Observation methods",
    color_discrete_sequence=["#2f8fd3"],
    labels={"Observation_Count": "Records", "Observation_Method": "Method"},
)
fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
st.plotly_chart(style_figure(fig, 560), use_container_width=True)
st.info(
    f"{latest_year} is partial and is excluded from the annual line. "
    "The near-uniform complete-year and method counts are further evidence of "
    "procedural data generation, not stable real-world sampling effort."
)
