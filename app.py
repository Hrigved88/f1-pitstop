import streamlit as st
import pandas as pd
import os
import base64
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="F1 Pit Stop Optimizer",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------
# CUSTOM CSS & BACKGROUND
# --------------------------
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: #e0e0e0;
            }}
            /* Make text readable and add some glassmorphism */
            [data-testid="stSidebar"] {{
                background-color: rgba(15, 17, 22, 0.85) !important;
                border-right: 1px solid rgba(255,255,255,0.1);
            }}
            div.css-1r6slb0.e1tzin5v2 {{
                background-color: rgba(0, 0, 0, 0.5);
                padding: 1rem;
                border-radius: 10px;
            }}
            h1, h2, h3, h4 {{
                color: #ffffff !important;
                font-family: 'Helvetica Neue', sans-serif;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                gap: 20px;
                background-color: rgba(0,0,0,0.3);
                padding: 10px;
                border-radius: 10px;
            }}
            .stTabs [data-baseweb="tab"] {{
                height: 50px;
                white-space: pre-wrap;
                background-color: rgba(255,255,255,0.05);
                border-radius: 5px;
                color: #fff;
                padding: 0 20px;
            }}
            .stTabs [aria-selected="true"] {{
                background-color: #e10600 !important;
                color: white !important;
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

def add_bg_from_url(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #e0e0e0;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Background function will be called after selecting the race.
# --------------------------
# LOAD DATA
# --------------------------
@st.cache_data
def load_data():
    data_path = "."
    try:
        lap_times = pd.read_csv(os.path.join(data_path, "lap_times.csv"))
        pit_stops = pd.read_csv(os.path.join(data_path, "pit_stops.csv"))
        drivers = pd.read_csv(os.path.join(data_path, "drivers.csv"))
        races = pd.read_csv(os.path.join(data_path, "races.csv"))
        results = pd.read_csv(os.path.join(data_path, "results.csv"))
        constructors = pd.read_csv(os.path.join(data_path, "constructors.csv"))
        return lap_times, pit_stops, drivers, races, results, constructors
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None

lap_times, pit_stops, drivers, races, results, constructors = load_data()

if lap_times is None:
    st.stop()

# --------------------------
# TEAM COLORS DICTIONARY
# --------------------------
# Expanded dictionary to handle common F1 constructors
TEAM_COLORS = {
    "Ferrari": "#dc0000",
    "Mercedes": "#00d2be",
    "Red Bull": "#0600ef",
    "McLaren": "#ff8700",
    "Alpine": "#0090ff",
    "Aston Martin": "#006f62",
    "Williams": "#005aff",
    "AlphaTauri": "#2b4562",
    "Haas": "#ffffff",
    "Alfa Romeo": "#900000",
    "Renault": "#fff500",
    "Toro Rosso": "#0000ff",
    "Racing Point": "#f596c8",
    "Force India": "#ff8e27",
    "Lotus": "#ffb800",
    "Sauber": "#006eff"
}

def get_team_color(constructor_name):
    for team, color in TEAM_COLORS.items():
        if team.lower() in constructor_name.lower():
            return color
    return "#e10600" # Default F1 red

# --------------------------
# TITLE & HEADER
# --------------------------
st.markdown("<h1 style='text-align: center; color: #e10600;'>🏎️ Formula 1 Pit Stop Optimizer</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 1.2rem; color: #cccccc;'>Analyze lap times, pit stops, and clustering strategies to optimize Formula 1 race performance.</p>", 
    unsafe_allow_html=True
)
st.markdown("---")

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg", width=100)
st.sidebar.markdown("## ⚙️ Dashboard Controls")

selected_driver = st.sidebar.selectbox("🏎️ Select Driver", drivers["surname"].unique())
selected_race = st.sidebar.selectbox("🏁 Select Race", races["name"].unique())

driver_id = drivers.loc[drivers["surname"] == selected_driver, "driverId"].values[0]
race_id = races.loc[races["name"] == selected_race, "raceId"].values[0]
circuit_id = races.loc[races["raceId"] == race_id, "circuitId"].values[0]

driver_laps = lap_times[(lap_times["driverId"] == driver_id) & (lap_times["raceId"] == race_id)]
driver_pits = pit_stops[(pit_stops["driverId"] == driver_id) & (pit_stops["raceId"] == race_id)]

# Determine driver's constructor/team for this race
driver_result = results[(results["driverId"] == driver_id) & (results["raceId"] == race_id)]
driver_team_name = "Unknown Team"
driver_color = "#e10600"

if not driver_result.empty:
    constructor_id = driver_result["constructorId"].values[0]
    team_row = constructors[constructors["constructorId"] == constructor_id]
    if not team_row.empty:
        driver_team_name = team_row["name"].values[0]
        driver_color = get_team_color(driver_team_name)

st.sidebar.markdown(f"**Team:** {driver_team_name}")
st.sidebar.markdown(f"<div style='width: 100%; height: 5px; background-color: {driver_color};'></div>", unsafe_allow_html=True)

# --------------------------
# DYNAMIC BACKGROUND LOGIC
# --------------------------
import json
bg_loaded = False
try:
    if os.path.exists("circuit_bg_map.json"):
        with open("circuit_bg_map.json", "r") as f:
            bg_map = json.load(f)
            str_circuit_id = str(circuit_id)
            if str_circuit_id in bg_map and bg_map[str_circuit_id]:
                add_bg_from_url(bg_map[str_circuit_id])
                bg_loaded = True
except Exception:
    pass

if not bg_loaded:
    # Determine the background based on circuit
    bg_image = "f1_bg.jpg" # Default

# 1. Street Circuits
street_circuits = [6, 73, 80, 82, 83] # Monaco, Baku, Las Vegas, Miami, Madrid etc.
# 2. Night / City Races
night_circuits = [15, 77] # Singapore, Jeddah
# 3. Desert Tracks
desert_circuits = [3, 24, 78] # Bahrain, Abu Dhabi, Qatar
# 4. Classic European / Forest Tracks
classic_circuits = [9, 10, 13, 14, 17, 21, 22, 1, 2, 7, 8, 11, 12, 18, 19, 20] # Silverstone, Spa, Monza, Albert Park, Sepang, Canada etc.

if circuit_id in street_circuits:
    bg_image = "bg_monaco.png"
elif circuit_id in night_circuits:
    bg_image = "bg_night.png"
elif circuit_id in desert_circuits:
    bg_image = "bg_desert.png"
elif circuit_id in classic_circuits:
    bg_image = "bg_classic.png"
else:
    # Use a modulo trick to randomly but consistently assign one of the 4 backgrounds to any other circuit
    fallback_bgs = ["bg_classic.png", "bg_desert.png", "bg_night.png", "bg_monaco.png"]
    bg_image = fallback_bgs[circuit_id % 4]
    
add_bg_from_local(bg_image)


# --------------------------
# KPI METRICS
# --------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_lap = f"{driver_laps['milliseconds'].mean() / 1000:.2f}s" if not driver_laps.empty else "N/A"
    st.markdown(f"<div class='metric-card'><h3>⏱️ Avg Lap Time</h3><h2>{avg_lap}</h2></div>", unsafe_allow_html=True)

with col2:
    fastest_lap = f"{driver_laps['milliseconds'].min() / 1000:.2f}s" if not driver_laps.empty else "N/A"
    st.markdown(f"<div class='metric-card'><h3>🔥 Fastest Lap</h3><h2>{fastest_lap}</h2></div>", unsafe_allow_html=True)

with col3:
    num_pits = str(len(driver_pits)) if not driver_pits.empty else "0"
    st.markdown(f"<div class='metric-card'><h3>🛑 Pit Stops</h3><h2>{num_pits}</h2></div>", unsafe_allow_html=True)

with col4:
    total_pit_time = f"{driver_pits['milliseconds'].sum() / 1000:.2f}s" if not driver_pits.empty else "0.0s"
    st.markdown(f"<div class='metric-card'><h3>🛠️ Total Pit Time</h3><h2>{total_pit_time}</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------
# MAIN TABS
# --------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Lap Time Analysis", "🛑 Pit Stop Analysis", "🔮 Pit Stop Strategy", "🧠 Clustering", "⚔️ Comparison"])

# Plotly Default Theme Configuration
px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = [driver_color, "#1f77b4", "#ff7f0e", "#2ca02c"]

with tab1:
    st.markdown("### 📊 Animated Lap Time Progression")
    st.markdown("Press the **Play** button below the chart to watch the driver's lap time progress through the race.")
    if not driver_laps.empty:
        # Sort and prepare data for animation
        plot_data = driver_laps.sort_values(by="lap").copy()
        
        # We need a dataframe where each frame contains data up to that lap
        # Plotly Express animation works best with scattered points, but we can animate a line using go.Figure
        
        # Simple go.Figure animated line
        fig = go.Figure(
            data=[go.Scatter(x=plot_data["lap"], y=plot_data["milliseconds"]/1000, mode="lines+markers", line=dict(color=driver_color, width=3))]
        )
        
        # Build frames for animation
        frames = [
            go.Frame(
                data=[go.Scatter(x=plot_data["lap"].iloc[:k+1], y=plot_data["milliseconds"].iloc[:k+1]/1000)],
                name=str(k+1)
            )
            for k in range(len(plot_data))
        ]
        fig.frames = frames
        
        # Add Play/Pause buttons
        fig.update_layout(
            updatemenus=[dict(
                type="buttons",
                bgcolor="#333333",
                font=dict(color="#ffffff"),
                buttons=[
                    dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                    dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))])
                ]
            )],
            xaxis=dict(title="Lap Number", range=[0, plot_data["lap"].max() + 2]),
            yaxis=dict(title="Lap Time (Seconds)", range=[(plot_data["milliseconds"].min()/1000) - 2, (plot_data["milliseconds"].max()/1000) + 2]),
            title=f"Animated Telemetry - {selected_driver} ({driver_team_name})",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No lap time data available for this driver in this race.")

with tab2:
    st.markdown("### 🛑 Pit Stop Analysis")
    if not driver_pits.empty:
        fig2 = px.bar(
            driver_pits, 
            x="lap", 
            y="milliseconds", 
            text="milliseconds",
            title=f"Pit Stops Duration - {selected_driver} at {selected_race}",
            labels={"milliseconds": "Pit Time (ms)", "lap": "Lap Number"}
        )
        # Apply team color to bars
        fig2.update_traces(marker_color=driver_color, texttemplate='%{text:.2s}', textposition='outside')
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff")
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No pit stop data available.")

with tab3:
    st.markdown("### 🔮 Pit Stop Strategy Prediction")
    st.markdown(f"**Circuit Insight:** Based on historical data for this circuit (*Circuit ID {circuit_id}*).")
    
    # Get all races for this circuit
    circuit_races = races[races["circuitId"] == circuit_id]["raceId"].unique()
    circuit_pits = pit_stops[pit_stops["raceId"].isin(circuit_races)]
    
    if not circuit_pits.empty:
        # Group pits by stop number (1st stop, 2nd stop)
        first_stops = circuit_pits[circuit_pits["stop"] == 1]
        
        if not first_stops.empty:
            median_lap = first_stops["lap"].median()
            q1 = first_stops["lap"].quantile(0.25)
            q3 = first_stops["lap"].quantile(0.75)
            
            st.success(f"🏎️ **Predicted Optimal Window for 1st Pit Stop:** Laps {int(q1)} - {int(q3)} (Median: Lap {int(median_lap)})")
            
            fig_hist = px.histogram(
                first_stops, 
                x="lap", 
                nbins=30,
                title="Historical 1st Pit Stop Laps at this Circuit",
                labels={"lap": "Lap Number", "count": "Frequency"},
                color_discrete_sequence=["#ffcc00"]
            )
            fig_hist.add_vline(x=median_lap, line_dash="dash", line_color="white", annotation_text="Median Pit Lap")
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff")
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Not enough data to calculate first pit stops for this circuit.")
    else:
        st.warning("No historical pit stop data found for this circuit.")

with tab4:
    st.markdown("### 🧠 Clustering Race Strategies")
    st.markdown("This uses **K-Means clustering** to group lap times, helping to identify **performance phases** (e.g., cruising, pushing, tire degradation).")
    if not driver_laps.empty:
        lap_data = driver_laps[["lap", "milliseconds"]].dropna()
        if len(lap_data) >= 3:
            kmeans = KMeans(n_clusters=3, random_state=42).fit(lap_data)
            lap_data["Cluster Phase"] = kmeans.labels_
            lap_data["Cluster Phase"] = lap_data["Cluster Phase"].map({0: "Phase A", 1: "Phase B", 2: "Phase C"})
            
            fig3 = px.scatter(
                lap_data, 
                x="lap", 
                y="milliseconds",
                color="Cluster Phase", 
                size="milliseconds",
                title=f"Lap Time Clustering - {selected_driver}",
                labels={"milliseconds": "Time (ms)", "lap": "Lap Number"}
            )
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff")
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Not enough data points for clustering.")
    else:
        st.info("No lap time data available for clustering.")

with tab5:
    st.markdown("### ⚔️ Driver Comparison")
    compare_driver = st.selectbox("Select Rival Driver to Compare", drivers["surname"].unique(), index=1)
    
    if compare_driver != selected_driver:
        comp_driver_id = drivers.loc[drivers["surname"] == compare_driver, "driverId"].values[0]
        comp_laps = lap_times[(lap_times["driverId"] == comp_driver_id) & (lap_times["raceId"] == race_id)]

        if not comp_laps.empty and not driver_laps.empty:
            driver_laps_comp = driver_laps.copy()
            driver_laps_comp["Driver"] = selected_driver
            comp_laps_comp = comp_laps.copy()
            comp_laps_comp["Driver"] = compare_driver
            
            combined_laps = pd.concat([driver_laps_comp, comp_laps_comp])
            
            # Fetch rival color
            rival_result = results[(results["driverId"] == comp_driver_id) & (results["raceId"] == race_id)]
            rival_color = "#ffffff"
            if not rival_result.empty:
                r_team_row = constructors[constructors["constructorId"] == rival_result["constructorId"].values[0]]
                if not r_team_row.empty:
                    rival_color = get_team_color(r_team_row["name"].values[0])
            
            fig4 = px.line(
                combined_laps,
                x="lap", 
                y="milliseconds", 
                color="Driver",
                title=f"Lap Time Comparison: {selected_driver} vs {compare_driver}",
                labels={"milliseconds": "Time (ms)", "lap": "Lap Number"},
                color_discrete_map={selected_driver: driver_color, compare_driver: rival_color}
            )
            fig4.update_layout(
                hovermode="x unified",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff")
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning(f"Comparison data unavailable for {compare_driver} in this race.")
    else:
        st.info("Select a different driver to compare.")

# --------------------------
# FOOTER
# --------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 0.9rem;'>"
    "Data Source: F1 Historical Dataset | Built with Streamlit 🚀"
    "</p>", 
    unsafe_allow_html=True
)
