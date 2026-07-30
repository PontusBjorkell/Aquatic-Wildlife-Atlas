import json

import plotly.express as px
import streamlit as st

from utils import DATA_DIR, configure_page, header, load_csv, style_figure

configure_page("Data Quality", "🔎")
header("Data Quality", "Completeness, taxonomy checks, and synthetic-pattern diagnostics.")
species = load_csv("species.csv")
coordinate = load_csv("coordinate_quality.csv")
report_path = DATA_DIR.parent / "processed" / "data_quality_report.json"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Missing cells", "0")
c2.metric("Duplicate IDs", "0")
c3.metric("Taxa", species.Scientific_Name.nunique())
c4.metric("Species epithets", species.Species_Epithet.nunique())

st.error(
    "The dataset should be treated as synthetic or template-generated: every "
    "taxon has 1,980–1,981 observations, no values are missing, and multiple "
    "ecological attributes are constant within every taxon."
)

balance = (
    species["Observation_Count"].value_counts().sort_index()
    .rename_axis("Observations per taxon").reset_index(name="Taxa")
)
balance["Observations per taxon"] = balance["Observations per taxon"].astype(str)
fig = px.bar(
    balance, x="Observations per taxon", y="Taxa", text="Taxa",
    title="Near-perfect observation balance across taxa",
)
fig.update_traces(textposition="outside")
st.plotly_chart(style_figure(fig, 380), use_container_width=True)

st.subheader("Ambiguous species epithets")
ambiguous = species[species.Species_Epithet.duplicated(False)][
    ["Species_Epithet", "Scientific_Name", "Common_Name"]
].sort_values("Species_Epithet")
st.dataframe(
    ambiguous.rename(columns={
        "Species_Epithet": "Species epithet",
        "Scientific_Name": "Scientific name",
        "Common_Name": "Common name",
    }),
    use_container_width=True, hide_index=True,
)

st.subheader("Coordinate dispersion within named locations")
st.dataframe(
    coordinate.rename(columns=lambda name: name.replace("_", " ")),
    use_container_width=True, hide_index=True,
)

if report_path.exists():
    with st.expander("Full machine-readable quality report"):
        st.json(json.loads(report_path.read_text()))
