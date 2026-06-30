import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.cluster import KMeans
import plotly.express as px

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="F1 Pit Stop Optimizer",
    layout="wide",
)

# --------------------------
import streamlit as st
import base64
import os

# Function to add background image (supports jpg)
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: white;  /* keeps text readable on dark bg */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Background image '{image_file}' not found.")

# Call the function with your jpg file
add_bg_from_local("f1_bg.jpg")
# --------------------------
# LOAD DATA
# --------------------------
data_path = r"your file directory path"

try:
    lap_times = pd.read_csv(os.path.join(data_path, "lap_times.csv"))
    pit_stops = pd.read_csv(os.path.join(data_path, "pit_stops.csv"))
    drivers = pd.read_csv(os.path.join(data_path, "drivers.csv"))
    races = pd.read_csv(os.path.join(data_path, "races.csv"))
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --------------------------
# TITLE
# --------------------------
st.title("🏎️ Formula 1 Pit Stop Optimizer Dashboard")

st.markdown(
    "This dashboard helps analyze **lap times, pit stops, and clustering strategies** "
    "to optimize Formula 1 race performance."
)

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.header("⚙️ Controls")
selected_driver = st.sidebar.selectbox("Select Driver", drivers["surname"].unique())
selected_race = st.sidebar.selectbox("Select Race", races["name"].unique())

# --------------------------
# LAP TIME ANALYSIS
# --------------------------
st.header(" Lap Time Analysis")

driver_id = drivers.loc[drivers["surname"] == selected_driver, "driverId"].values[0]
race_id = races.loc[races["name"] == selected_race, "raceId"].values[0]

driver_laps = lap_times[(lap_times["driverId"] == driver_id) & (lap_times["raceId"] == race_id)]

if not driver_laps.empty:
    fig = px.line(driver_laps, x="lap", y="milliseconds", title=f"Lap Times - {selected_driver} at {selected_race}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No lap time data available for this driver in this race.")

# --------------------------
# PIT STOP ANALYSIS
# --------------------------
st.header(" Pit Stop Analysis")

driver_pits = pit_stops[(pit_stops["driverId"] == driver_id) & (pit_stops["raceId"] == race_id)]

if not driver_pits.empty:
    fig2 = px.bar(driver_pits, x="lap", y="milliseconds", title=f"Pit Stops - {selected_driver} at {selected_race}")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No pit stop data available.")

# --------------------------
# CLUSTERING STRATEGY
# --------------------------
st.header(" Clustering Race Strategies")

if not driver_laps.empty:
    lap_data = driver_laps[["lap", "milliseconds"]].dropna()
    kmeans = KMeans(n_clusters=3, random_state=42).fit(lap_data)
    lap_data["Cluster"] = kmeans.labels_

    fig3 = px.scatter(
        lap_data, x="lap", y="milliseconds",
        color="Cluster", title=f"Lap Time Clustering - {selected_driver}"
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Not enough lap time data for clustering.")

# --------------------------
# COMPARISON DASHBOARD
# --------------------------
st.header(" Driver Comparison")

compare_driver = st.selectbox("Compare with Driver", drivers["surname"].unique())

if compare_driver != selected_driver:
    comp_driver_id = drivers.loc[drivers["surname"] == compare_driver, "driverId"].values[0]
    comp_laps = lap_times[(lap_times["driverId"] == comp_driver_id) & (lap_times["raceId"] == race_id)]

    if not comp_laps.empty and not driver_laps.empty:
        fig4 = px.line(
            pd.concat([
                driver_laps.assign(Driver=selected_driver),
                comp_laps.assign(Driver=compare_driver)
            ]),
            x="lap", y="milliseconds", color="Driver",
            title=f"Lap Time Comparison - {selected_driver} vs {compare_driver}"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Comparison data unavailable.")

# --------------------------
# RESULTS
# --------------------------
st.header(" Insights & Results")

st.markdown("""
- Drivers with **consistent lap times** tend to perform better overall.  
- Pit stop timing and duration significantly impact race results.  
- Clustering reveals **performance phases** (early, mid, late race).  
- Comparisons help in strategy planning between teammates and rivals.  
""")
