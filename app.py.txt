"""
app.py — Main Streamlit Dashboard
Diabetes Health Indicators — BRFSS 2015
Course: Exploratory Data Analysis | Instructor: Ali Hassan Sherazi
"""

import streamlit as st
import pandas as pd
import numpy as np

from filters import (load_data, apply_filters, get_kpis,
                     DATASET_OPTIONS, AGE_LABELS, GENHLTH_LABELS)
from charts import (pie_chart, histogram, line_chart, bar_chart,
                    scatter_plot, box_plot, heatmap, area_chart,
                    count_plot, violin_plot, pair_plot)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diabetes Health Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F9FA; }
    .block-container { padding-top: 1.5rem; }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #2E86AB;
    }
    .kpi-value { font-size: 28px; font-weight: 700; color: #2E86AB; }
    .kpi-label { font-size: 12px; color: #888; margin-top: 4px; }
    .section-title {
        font-size: 20px; font-weight: 700;
        color: #1A1A2E; margin: 24px 0 12px 0;
        border-bottom: 3px solid #2E86AB;
        padding-bottom: 6px;
    }
    [data-testid="stSidebar"] { background-color: #1A1A2E; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #AAD4F5 !important; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR — Dataset selector + Filters ──────────────────────────────────────
with st.sidebar:
    st.markdown("## 🩺 Diabetes Dashboard")
    st.markdown("---")

    # Dataset selector
    dataset_choice = st.selectbox("📂 Select Dataset", list(DATASET_OPTIONS.keys()))
    filepath = DATASET_OPTIONS[dataset_choice]

    # Load data (cached)
    @st.cache_data(show_spinner="Loading data…")
    def get_data(fp):
        return load_data(fp)

    df_full = get_data(filepath)

    st.markdown("---")
    st.markdown("### 🔽 Filters")

    # Category filter — Diabetes status
    diabetes_options = df_full["Diabetes_Label"].unique().tolist()
    diabetes_filter = st.multiselect(
        "Diabetes Status", diabetes_options, default=diabetes_options,
        help="Multi-select filter"
    )

    # Sex filter
    sex_options = df_full["Sex_Label"].unique().tolist()
    sex_filter = st.multiselect(
        "Sex", sex_options, default=sex_options
    )

    # Age range slider
    age_min, age_max = int(df_full["Age"].min()), int(df_full["Age"].max())
    age_range = st.slider(
        "Age Group (1=18-24 … 13=80+)",
        min_value=age_min, max_value=age_max,
        value=(age_min, age_max)
    )

    # BMI range slider
    bmi_min, bmi_max = float(df_full["BMI"].min()), float(df_full["BMI"].max())
    bmi_range = st.slider(
        "BMI Range",
        min_value=bmi_min, max_value=bmi_max,
        value=(bmi_min, min(bmi_max, 60.0))
    )

    # General health filter
    genhlth_options = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
    genhlth_filter = st.multiselect(
        "General Health", genhlth_options, default=genhlth_options
    )

    # Text search filter
    search_text = st.text_input("🔍 Search / Text Filter", value="",
                                 placeholder="e.g. 1.0")

    # Reset button
    if st.button("🔄 Reset All Filters"):
        st.rerun()

    st.markdown("---")
    st.markdown("<small>Course: Exploratory Data Analysis<br>Instructor: Ali Hassan Sherazi<br>Dataset: BRFSS 2015</small>",
                unsafe_allow_html=True)

# ── Apply filters ──────────────────────────────────────────────────────────────
df = apply_filters(
    df_full,
    diabetes_filter=diabetes_filter,
    sex_filter=sex_filter,
    age_range=age_range,
    bmi_range=bmi_range,
    genhlth_filter=genhlth_filter,
    search_text=search_text
)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#1A1A2E,#2E86AB);
            padding:28px 32px; border-radius:14px; margin-bottom:20px;'>
    <h1 style='color:white;margin:0;font-size:32px;'>🩺 Diabetes Health Indicators Dashboard</h1>
    <p style='color:#AAD4F5;margin:6px 0 0 0;font-size:15px;'>
        BRFSS 2015 Survey · Exploratory Data Analysis · Interactive Visualization
    </p>
</div>
""", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("⚠️ No records match the current filters. Please adjust the filters.")
    st.stop()

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
kpis = get_kpis(df)
cols = st.columns(len(kpis))
kpi_colors = ["#2E86AB", "#E84855", "#3BB273", "#F4A261", "#9B5DE5", "#F15BB5"]
for i, (label, value) in enumerate(kpis.items()):
    with cols[i]:
        st.markdown(f"""
        <div class='kpi-card' style='border-left-color:{kpi_colors[i]}'>
            <div class='kpi-value' style='color:{kpi_colors[i]}'>{value}</div>
            <div class='kpi-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHART TABS ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Distribution Charts",
    "📈 Trend & Relationship Charts",
    "🔥 Statistical Charts",
    "🗺️ Categorical Charts",
    "🎯 Bonus Charts"
])

# TAB 1: Distribution
with tab1:
    st.markdown("<div class='section-title'>Distribution Analysis</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Pie Chart** — Diabetes Status Proportions")
        st.pyplot(pie_chart(df), use_container_width=True)
    with c2:
        st.markdown("**2. Histogram** — BMI Frequency Distribution")
        st.pyplot(histogram(df), use_container_width=True)

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**6. Box Plot** — BMI Spread & Outliers")
        st.pyplot(box_plot(df), use_container_width=True)
    with c4:
        st.markdown("**10. Violin Plot** — BMI Probability Density")
        st.pyplot(violin_plot(df), use_container_width=True)

# TAB 2: Trend & Relationship
with tab2:
    st.markdown("<div class='section-title'>Trends & Relationships</div>", unsafe_allow_html=True)
    st.markdown("**3. Line Chart** — Diabetes Trend Across Age Groups")
    st.pyplot(line_chart(df), use_container_width=True)

    st.markdown("---")
    st.markdown("**5. Scatter Plot** — BMI vs Mental Health Days")
    st.pyplot(scatter_plot(df), use_container_width=True)

    st.markdown("---")
    st.markdown("**8. Area Chart** — Cumulative Cases by Age Group")
    st.pyplot(area_chart(df), use_container_width=True)

# TAB 3: Statistical
with tab3:
    st.markdown("<div class='section-title'>Correlation & Statistical Analysis</div>", unsafe_allow_html=True)
    st.markdown("**7. Heatmap** — Feature Correlation Matrix")
    st.pyplot(heatmap(df), use_container_width=True)

# TAB 4: Categorical
with tab4:
    st.markdown("<div class='section-title'>Categorical Analysis</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**4. Bar Chart** — Risk Factor Prevalence")
        st.pyplot(bar_chart(df), use_container_width=True)
    with c2:
        st.markdown("**9. Count Plot** — General Health Category Counts")
        st.pyplot(count_plot(df), use_container_width=True)

    # Education vs Diabetes grouped bar
    st.markdown("---")
    st.markdown("**Extra: Diabetes Rate by Education Level**")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from filters import EDUCATION_LABELS
    edu_diab = df.groupby("Education_Label")["Diabetes_binary"].apply(
        lambda x: (x > 0).mean() * 100
    ).reset_index()
    edu_diab.columns = ["Education", "Diabetes Rate (%)"]
    edu_order = list(EDUCATION_LABELS.values())
    edu_diab["Education"] = pd.Categorical(edu_diab["Education"], categories=edu_order, ordered=True)
    edu_diab = edu_diab.sort_values("Education")
    fig, ax = plt.subplots(figsize=(9, 4), facecolor="white")
    ax.bar(edu_diab["Education"], edu_diab["Diabetes Rate (%)"],
           color="#2E86AB", edgecolor="white")
    ax.set_title("Diabetes Rate by Education Level", fontsize=13, fontweight="bold")
    ax.set_xlabel("Education Level")
    ax.set_ylabel("Diabetes Rate (%)")
    ax.set_xticklabels(edu_diab["Education"], rotation=20, ha="right")
    ax.grid(axis="y", color="#EEEEEE")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# TAB 5: Bonus
with tab5:
    st.markdown("<div class='section-title'>Bonus Visualizations</div>", unsafe_allow_html=True)
    st.markdown("**Bonus: Pair Plot** — Multi-feature Relationship")
    with st.spinner("Rendering pair plot (may take a moment)…"):
        st.pyplot(pair_plot(df), use_container_width=True)

# ── RAW DATA PREVIEW ──────────────────────────────────────────────────────────
with st.expander("📋 View Raw Filtered Data"):
    st.dataframe(df.head(500), use_container_width=True)
    st.caption(f"Showing first 500 of {len(df):,} filtered records.")