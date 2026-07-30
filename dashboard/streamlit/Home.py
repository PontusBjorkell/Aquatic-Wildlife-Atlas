"""Executive landing page for the Aquatic Wildlife Atlas."""

import plotly.express as px
import streamlit as st

from utils import (
    IUCN_COLORS, IUCN_ORDER, caveat, configure_page, header, load_csv,
    style_figure,
)

configure_page("Aquatic Wildlife Atlas")
header(
    "Aquatic Wildlife Atlas",
    "An end-to-end biodiversity analytics portfolio: Python, SQL, statistics, "
    "Streamlit, and Tableau.",
)
caveat()

summary = load_csv("executive_summary.csv").iloc[0]
species = load_csv("species.csv")
conservation = load_csv("conservation.csv")
annual = load_csv("annual_trends.csv")

cols = st.columns(5)
cols[0].metric("Observations", f"{summary.Observation_Count:,.0f}")
cols[1].metric("Taxa", f"{summary.Taxon_Count:,.0f}")
cols[2].metric("Classes", f"{summary.Class_Count:,.0f}")
cols[3].metric("Locations", f"{summary.Location_Count:,.0f}")
cols[4].metric("Threatened taxa", f"{summary.Threatened_Taxon_Count:,.0f}")

left, right = st.columns([1.05, 1])
with left:
    fig = px.bar(
        conservation,
        x="IUCN_Status",
        y="Taxon_Count",
        color="IUCN_Status",
        category_orders={"IUCN_Status": IUCN_ORDER},
        color_discrete_map=IUCN_COLORS,
        title="Taxa by conservation status",
        labels={"IUCN_Status": "IUCN status", "Taxon_Count": "Taxa"},
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)
with right:
    class_counts = species["Class"].value_counts().head(10).reset_index()
    fig = px.bar(
        class_counts,
        x="count",
        y="Class",
        orientation="h",
        title="Largest taxonomic classes",
        color="count",
        color_continuous_scale="Teal",
        labels={"count": "Taxa"},
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)

latest_year = int(annual["Observation_Year"].max())
complete = annual[annual["Observation_Year"] < latest_year]
partial = annual.loc[annual["Observation_Year"] == latest_year].iloc[0]
fig = px.line(
    complete,
    x="Observation_Year",
    y="Observation_Count",
    markers=True,
    title=f"Observation records by complete year (through {latest_year - 1})",
    labels={"Observation_Year": "Year", "Observation_Count": "Records"},
)
st.plotly_chart(style_figure(fig, 400), use_container_width=True)
st.caption(
    f"{latest_year} is excluded from the trend because it is a partial year "
    f"({partial.Observation_Count:,.0f} records in the supplied data)."
)

st.info(
    "Use the pages in the sidebar to explore species, conservation, "
    "distribution, environmental conditions, biological traits, observation "
    "trends, and data quality."
)
