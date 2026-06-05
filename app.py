import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Diabetes Health Indicators Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global styling for charts to match the report look
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'figure.titlesize': 13,
    'axes.titleweight': 'bold'
})

# Mapping dictionaries for readable charts
AGE_MAPPING = {
    1: "18-24", 2: "25-29", 3: "30-34", 4: "35-39", 5: "40-44", 
    6: "45-49", 7: "50-54", 8: "55-59", 9: "60-64", 10: "65-69", 
    11: "70-74", 12: "75-79", 13: "80+"
}

GEN_HEALTH_MAPPING = {
    1: "1 - Excellent", 2: "2 - Very Good", 3: "3 - Good", 4: "4 - Fair", 5: "5 - Poor"
}

# ==========================================
# 2. DATA LOADING FUNCTION (CACHED)
# ==========================================
@st.cache_data
def load_selected_data(dataset_choice):
    if dataset_choice == "Standard Population Dataset (Imbalanced)":
        filename = "diabetes_012_health_indicators_BRFSS2015.csv"
    else:
        filename = "diabetes_binary_5050split_health_indicators_BRFSS2015.csv"
        
    try:
        df = pd.read_csv(filename)
        
        # Determine target column name based on dataset
        target_col = 'Diabetes_012' if 'Diabetes_012' in df.columns else 'Diabetes_binary'
        
        # Map target labels dynamically
        if target_col == 'Diabetes_012':
            df['Diabetes_Label'] = df[target_col].map({0.0: 'No Diabetes', 1.0: 'Pre-Diabetes', 2.0: 'Diabetes'})
        else:
            df['Diabetes_Label'] = df[target_col].map({0.0: 'No Diabetes', 1.0: 'Diabetes'})
            
        # Map structural columns for visualization readability
        df['AgeGroup'] = df['Age'].map(AGE_MAPPING)
        df['GeneralHealth'] = df['GenHlth'].map(GEN_HEALTH_MAPPING)
        
        return df, target_col
    except FileNotFoundError:
        st.error(f"❌ Error: '{filename}' file nahi mili! Kindly check step 1 project folder.")
        st.stop()

# ==========================================
# 3. SIDEBAR CONTROLS & FILTERS
# ==========================================
st.sidebar.header("⚙️ Dashboard Controls")

# A. Dataset Dropdown Selector
dataset_mode = st.sidebar.selectbox(
    "Choose Analysis Dataset:",
    options=[
        "Standard Population Dataset (Imbalanced)", 
        "Balanced 50/50 Split Dataset"
    ]
)

# Load data based on selection
df, target_column = load_selected_data(dataset_mode)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Demographic & Risk Filters")

# B. Age Group Multi-Select Filter
all_age_groups = list(AGE_MAPPING.values())
selected_ages = st.sidebar.multiselect(
    "Select Age Groups:",
    options=all_age_groups,
    default=all_age_groups
)

# C. Sex Filter (0 = Female, 1 = Male)
sex_choice = st.sidebar.radio(
    "Gender Filter:",
    options=["All", "Female Only", "Male Only"],
    index=0
)

# Apply filters dynamically to the dataframe
filtered_df = df[df['AgeGroup'].isin(selected_ages)] if selected_ages else df

if sex_choice == "Female Only":
    filtered_df = filtered_df[filtered_df['Sex'] == 0.0]
elif sex_choice == "Male Only":
    filtered_df = filtered_df[filtered_df['Sex'] == 1.0]

# ==========================================
# 4. MAIN HEADERS & KEY METRICS (KPIs)
# ==========================================
st.title("🩸 Comprehensive Diabetes Patient Analysis Dashboard")
st.markdown(f"**Active View:** `{dataset_mode}` based on CDC's BRFSS Survey.")
st.write("---")

# KPI Section
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(label="👥