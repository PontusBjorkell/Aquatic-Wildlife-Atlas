import plotly.express as px
import streamlit as st

from utils import IUCN_COLORS, IUCN_ORDER, caveat, configure_page, header, load_csv, style_figure

configure_page("Conservation Overview", "🛟")
header("Conservation Overview", "Taxon-level status patterns and threatened groups.")
caveat()
species = load_csv("species.csv")
summary = load_csv("conservation.csv")
summary["IUCN_Status"] = summary["IUCN_Status"].astype(str)

c1, c2, c3 = st.columns(3)
c1.metric("Threatened taxa", int(species["Is_Threatened"].sum()))
c2.metric("Critically endangered", int((species.IUCN_Status == "Critically Endangered").sum()))
c3.metric("Unassessed / uncertain", int(species.IUCN_Status.isin(["Not Evaluated", "Data Deficient"]).sum()))

left, right = st.columns(2)
with left:
    fig = px.bar(
        summary, x="IUCN_Status", y="Taxon_Count", color="IUCN_Status",
        category_orders={"IUCN_Status": IUCN_ORDER},
        color_discrete_map=IUCN_COLORS, title="Conservation-status composition",
        labels={"IUCN_Status": "IUCN status", "Taxon_Count": "Taxa"},
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)
with right:
    grouped = species.groupby("Class", as_index=False).agg(
        Taxa=("Scientific_Name", "count"), Threatened=("Is_Threatened", "sum")
    )
    grouped["Threatened_Percentage"] = 100 * grouped.Threatened / grouped.Taxa
    chart_data = grouped[grouped["Taxa"] >= 3]
    fig = px.bar(
        chart_data.sort_values("Threatened_Percentage"),
        x="Threatened_Percentage", y="Class", orientation="h",
        color="Taxa", title="Threatened share by class (at least 3 taxa)",
        labels={"Threatened_Percentage": "Threatened taxa (%)"},
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)

threatened = species.loc[species["Is_Threatened"].astype(bool)].sort_values(
    ["IUCN_Risk_Score", "Common_Name"], ascending=[False, True]
)
st.subheader("Threatened taxa")
st.dataframe(
    threatened[
        ["Common_Name", "Scientific_Name", "Class", "Habitat_Type", "IUCN_Status"]
    ].rename(columns={
        "Common_Name": "Common name", "Scientific_Name": "Scientific name",
        "Habitat_Type": "Habitat", "IUCN_Status": "IUCN status",
    }),
    use_container_width=True, hide_index=True,
)
