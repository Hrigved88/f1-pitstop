# 🏎️ Formula 1 Pit Stop Optimizer Dashboard

Welcome to the **Formula 1 Pit Stop Optimizer**, a comprehensive data visualization dashboard built with Python and Streamlit. This application analyzes historical Formula 1 race data to optimize pit stop strategies, visualize lap times, and provide in-depth performance metrics for drivers and constructors.

## ✨ Key Features

*   **Dynamic Photorealistic Backgrounds:** The dashboard automatically changes its background to match the selected race! It features a curated mapping of 79 unique F1 circuits, accurately displaying night races, street circuits, desert tracks, and classic European circuits with real aerial photographs.
*   **Premium Glassmorphic UI:** A beautifully customized Dark Theme UI with glass-like translucent panels, ensuring high readability and a modern, state-of-the-art aesthetic.
*   **KPI Metrics Dashboard:** Instant top-level insights showing Average Lap Time, Fastest Lap, Total Pit Stops, and Total Pit Time at a glance.
*   **Advanced Telemetry Visualizations:** Interactive Plotly charts allowing you to analyze lap time consistency, tire degradation, and comparative performance between drivers.
*   **K-Means Strategy Clustering:** Employs Machine Learning (`scikit-learn`) to cluster pit stop strategies based on lap times and durations, identifying the most optimal strategies for a given race.
*   **Team Colors:** Automatically color-codes data visualizations using the official F1 Constructor hex colors (e.g., Red Bull Blue, Ferrari Red, Mercedes Silver) for immediate recognition.

## 🛠️ Technology Stack

*   **Python** (Core Logic)
*   **Streamlit** (Web Application Framework)
*   **Pandas** (Data Manipulation & Caching)
*   **Plotly Express** (Interactive Charting)
*   **Scikit-Learn** (K-Means Machine Learning)

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Hrigved88/f1-pitstop.git
    cd f1-pitstop
    ```

2.  **Install the required dependencies:**
    Ensure you have Python installed, then run:
    ```bash
    pip install streamlit pandas plotly scikit-learn
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    The application will automatically open in your default web browser at `http://localhost:8501`.

## 📁 Dataset
This dashboard relies on historical Formula 1 data files (e.g., `lap_times.csv`, `pit_stops.csv`, `circuits.csv`, `results.csv`, `constructors.csv`). Ensure all CSV files are located in the root directory for the application to function correctly.
