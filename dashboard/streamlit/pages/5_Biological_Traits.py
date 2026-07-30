import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import configure_page, header, load_csv, species_filters, style_figure

configure_page("Biological Traits", "🐋")
header("Biological Traits", "Morphology, longevity, diet, and allometric structure.")
species = species_filters(load_csv("species.csv"), "traits")

fig = px.scatter(
    species, x="Mean_Body_Length_cm", y="Mean_Body_Weight_kg",
    color="Diet", hover_name="Common_Name",
    hover_data=["Scientific_Name", "Class", "IUCN_Status"],
    log_x=True, log_y=True,
    title="Length–weight relationship (log scales)",
    labels={
        "Mean_Body_Length_cm": "Mean body length (cm)",
        "Mean_Body_Weight_kg": "Mean body weight (kg)",
    },
)
positive = species[
    (species["Mean_Body_Length_cm"] > 0) & (species["Mean_Body_Weight_kg"] > 0)
]
if not positive.empty:
    fitted_x = np.geomspace(
        positive["Mean_Body_Length_cm"].min(),
        positive["Mean_Body_Length_cm"].max(),
        150,
    )
    fitted_y = 10 ** (-3.952991 + 2.532592 * np.log10(fitted_x))
    fig.add_trace(go.Scatter(
        x=fitted_x, y=fitted_y, mode="lines", name="Global allometric fit",
        line={"color": "#111827", "width": 3, "dash": "dash"},
    ))
st.plotly_chart(style_figure(fig, 550), use_container_width=True)
st.caption(
    "Validated taxon-level model: log10(weight) ~ log10(length), "
    "slope ≈ 2.533 and R² ≈ 0.888."
)

left, right = st.columns(2)
with left:
    fig = px.box(
        species, x="Diet", y="Mean_Body_Length_cm",
        points="all", log_y=True, title="Body length by diet",
        labels={"Mean_Body_Length_cm": "Mean body length (cm)"},
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)
with right:
    fig = px.scatter(
        species, x="Mean_Estimated_Age_yr", y="Mean_Body_Weight_kg",
        color="Class", hover_name="Common_Name", log_y=True,
        title="Longevity and body weight",
        labels={
            "Mean_Estimated_Age_yr": "Mean estimated age (years)",
            "Mean_Body_Weight_kg": "Mean body weight (kg)",
        },
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)

st.subheader("Largest taxa")
st.dataframe(
    species.nlargest(20, "Mean_Body_Length_cm")[
        ["Common_Name", "Scientific_Name", "Mean_Body_Length_cm", "Mean_Body_Weight_kg"]
    ].rename(columns={
        "Common_Name": "Common name", "Scientific_Name": "Scientific name",
        "Mean_Body_Length_cm": "Mean length (cm)",
        "Mean_Body_Weight_kg": "Mean weight (kg)",
    }), use_container_width=True, hide_index=True,
)
