"""Shared Streamlit helpers and visual design."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "dashboard"
IUCN_ORDER = [
    "Not Evaluated", "Data Deficient", "Least Concern", "Near Threatened",
    "Vulnerable", "Endangered", "Critically Endangered",
]
IUCN_COLORS = {
    "Not Evaluated": "#94a3b8", "Data Deficient": "#64748b",
    "Least Concern": "#22c55e", "Near Threatened": "#eab308",
    "Vulnerable": "#f97316", "Endangered": "#ef4444",
    "Critically Endangered": "#991b1b",
}


def configure_page(title: str, icon: str = "🌊") -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.6rem; padding-bottom: 3rem;}
        [data-testid="stMetric"] {
            background: linear-gradient(135deg,#0f2942,#123b5d);
            border: 1px solid #24577c; border-radius: 12px; padding: 14px;
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
            color: #f4fbff;
        }
        .caveat {background:#fff7ed;color:#7c2d12;border-left:5px solid #f97316;
                 padding:1rem;border-radius:8px;margin:1rem 0;}
        .subtitle {color:#6b7280;font-size:1.05rem;margin-top:-0.6rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        st.error(
            f"Missing dashboard data: {filename}. "
            "Run `python scripts/export_dashboard_data.py`."
        )
        st.stop()
    df = pd.read_csv(path)
    if "Is_Threatened" in df.columns:
        numeric = pd.to_numeric(df["Is_Threatened"], errors="coerce")
        if numeric.notna().all():
            df["Is_Threatened"] = numeric.eq(1)
        else:
            df["Is_Threatened"] = (
                df["Is_Threatened"].astype(str).str.strip().str.lower()
                .isin({"true", "yes", "y", "1"})
            )
    return df


def header(title: str, subtitle: str) -> None:
    st.title(title)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)


def caveat() -> None:
    st.markdown(
        '<div class="caveat"><b>Interpretation boundary:</b> This educational '
        "dataset has strong template-generated patterns. Visuals describe the "
        "supplied records and are not population estimates or verified "
        "ecological evidence.</div>",
        unsafe_allow_html=True,
    )


def style_figure(fig, height: int = 460):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="",
    )
    return fig


def download_csv(df: pd.DataFrame, label: str, filename: str) -> None:
    st.download_button(
        label,
        df.to_csv(index=False).encode("utf-8"),
        filename,
        "text/csv",
    )


def species_filters(df: pd.DataFrame, key: str) -> pd.DataFrame:
    c1, c2, c3, c4 = st.columns(4)
    classes = c1.multiselect(
        "Class", sorted(df["Class"].unique()), key=f"{key}_class"
    )
    habitats = c2.multiselect(
        "Habitat", sorted(df["Habitat_Type"].unique()), key=f"{key}_habitat"
    )
    statuses = c3.multiselect(
        "IUCN status", IUCN_ORDER, key=f"{key}_status"
    )
    diets = c4.multiselect(
        "Diet", sorted(df["Diet"].unique()), key=f"{key}_diet"
    )
    filtered = df.copy()
    for column, values in [
        ("Class", classes), ("Habitat_Type", habitats),
        ("IUCN_Status", statuses), ("Diet", diets),
    ]:
        if values:
            filtered = filtered[filtered[column].isin(values)]
    return filtered


def no_data(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No records match the current filters.")
        st.stop()
