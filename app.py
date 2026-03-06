# app.py
import networkx
import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import numpy as np

from city import City
from vehicles import Vehicle
from simulation import Simulation

st.set_page_config(layout="wide", page_title="Dashboard")


ADDRESS = "1449 Primrose Way, Cupertino, CA"

# 1. CACHE THE CITY LOADING (Crucial for Streamlit)
@st.cache_resource
def init_city_and_sim():
    city = City()
    city.load_city_from_address(ADDRESS, radius=2000)
    
    vehicles = []
    # Initialize your 100 vehicles like you did in run()
    for i in range(100):
        x, y = city.get_random_point()
        vehicles.append(Vehicle(x=x, y=y, vehicle_id=i, speed_mps=12))
        
    sim = Simulation(city, vehicles)
    
    # Assign some random initial routes
    x_min, x_max, y_min, y_max = -122.42, -122.38, 37.78, 37.80 # Approximate SF bounds
    for _ in range(50):
        try:
            x,y = city.get_random_point()
            x2,y2 = city.get_random_point()
            v = vehicles[int(np.random.uniform(0, len(vehicles)-1))]
            start = (y, x)
            end = (y2, x2)
            # for _ in range(1000):
            try:
                v.assign_route(city.get_route(start, end))
            except networkx.exception.NetworkXNoPath:
                print("No path found for random route, skipping assignment")

            route = city.get_route(start, end)
            v.assign_route(route)
        except Exception:
            pass

    return city, sim

city, sim = init_city_and_sim()

# 2. BUILD THE UI LAYOUT
st.title("Fleet Orchestration")
col1, col2, col3 = st.columns(3)
metric_time = col1.empty()
metric_active = col2.empty()
metric_idle = col3.empty()

# This is where the map will be drawn
map_placeholder = st.empty()

st.markdown("---") # Adds a nice horizontal divider line
st.subheader("System Analytics")

# Create a new row with two columns (making the chart wider than the table)
bottom_col1, bottom_col2 = st.tabs(["Vehicle Activity Over Time", "Current Vehicle Status"]) 

with bottom_col1:
    chart_placeholder = st.empty()
with bottom_col2:
    table_placeholder = st.empty()

history_data = []

# Controls
start_sim = st.sidebar.button("Start Simulation")
stop_sim = st.sidebar.button("Stop Simulation")

if "running" not in st.session_state:
    st.session_state.running = False

if start_sim:
    st.session_state.running = True
if stop_sim:
    st.session_state.running = False

# 3. THE MAIN SIMULATION LOOP
if st.session_state.running:
    # Use a while loop inside Streamlit to act like FuncAnimation
    while st.session_state.running:
        sim.step()
        
        # Get data and create DataFrame
        vehicle_data = sim.get_vehicle_data()
        df = pd.DataFrame(vehicle_data)

        table_placeholder.dataframe(df.drop(columns=['color']), height=500, hide_index=True)
        
        # 4. Update the Line Chart
        active_count = len(df[df['status'] != 'VehicleStatus.IDLE'])
        idle_count = len(df[df['status'] == 'VehicleStatus.IDLE'])
        
        # Append this frame's data to our history
        history_data.append({"Time": sim.time, "Active": active_count, "Idle": idle_count})
        
        # Convert history to a dataframe and plot it
        history_df = pd.DataFrame(history_data).set_index("Time")
        chart_placeholder.line_chart(history_df)
        
        # Update Metrics
        metric_time.metric("Sim Time", f"{sim.time:.1f}s")
        metric_active.metric("Active Cars", len(df[df['status'] != 'VehicleStatus.IDLE']))
        metric_idle.metric("Idle Cars", len(df[df['status'] == 'VehicleStatus.IDLE']))

        # Define the PyDeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position="[lon, lat]",
            get_color="color",
            get_radius=10,
            pickable=True,
            extruded=True,
        )

        # Set the viewport to match your loaded city
        view_state = pdk.ViewState(
            latitude=37.31, # SF
            longitude=-122.02, # SF
            zoom=13,
            pitch=45, # 3D tilt!
            bearing=0,
        )

        # Render the map to the placeholder
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Vehicle ID: {id}\nStatus: {status}"}, map_style='road')
        map_placeholder.pydeck_chart(r)
        
        # Throttle the loop so it doesn't crash your browser
        time.sleep(0.05)