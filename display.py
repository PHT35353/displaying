import requests
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Streamlit app title
st.title("Dynamic Map Display with CSV Integration")

# Backend URLs
FASTAPI_URL = "http://127.0.0.1:8000"  # Replace with your FastAPI backend URL
MAP_SETTINGS_ENDPOINT = f"{FASTAPI_URL}/map-settings"
PROCESS_CSV_ENDPOINT = f"{FASTAPI_URL}/process-csv"

# Step 1: Fetch map settings from backend
response = requests.get(MAP_SETTINGS_ENDPOINT)
if response.status_code == 200:
    map_settings = response.json()
    mapbox_token = map_settings["mapbox_access_token"]
    center_coords = map_settings["center_coordinates"]
    zoom_level = map_settings["zoom_level"]
else:
    st.error("Failed to fetch map settings from backend.")
    st.stop()

# Step 2: Initialize the folium map with Mapbox settings
folium_map = folium.Map(
    location=center_coords,
    zoom_start=zoom_level,
    tiles=f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}",
    attr="Mapbox Satellite | &copy; <a href='https://www.mapbox.com/about/maps/'>Mapbox</a>"
)

# Step 3: Upload the .csv file
csv_file = st.file_uploader("Upload the .csv file containing the pipe and landmark data", type=["csv"])

if csv_file:
    # Send the file to the backend for processing
    files = {"file": csv_file.getvalue()}
    response = requests.post(PROCESS_CSV_ENDPOINT, files=files)

    if response.status_code == 200 and response.json().get("status") == "success":
        data = response.json()["data"]
        st.write("Processed Data:")
        st.dataframe(pd.DataFrame(data))

        # Add a marker cluster for landmarks
        marker_cluster = MarkerCluster().add_to(folium_map)

        # Add pipes and landmarks from processed data
        for item in data:
            coords = item["Coordinates"]
            name = item["Name"]
            if item.get("Length (meters)", 0) > 0:  # Pipe
                popup_content = f"""
                <b>Name:</b> {name}<br>
                <b>Length:</b> {item.get("Length (meters)", "N/A")} meters<br>
                <b>Medium:</b> {item.get("Medium", "N/A")}<br>
                <b>Coordinates:</b> {coords}
                """
                folium.PolyLine(
                    locations=coords,
                    color="blue",
                    weight=3,
                    tooltip=name,
                    popup=folium.Popup(popup_content, max_width=300),
                ).add_to(folium_map)
            else:  # Landmark
                popup_content = f"""
                <b>Name:</b> {name}<br>
                <b>Coordinates:</b> {coords[0]}
                """
                folium.Marker(
                    location=coords[0],
                    icon=folium.Icon(color="green", icon="info-sign"),
                    tooltip=f"Landmark: {name}",
                    popup=folium.Popup(popup_content, max_width=300),
                ).add_to(marker_cluster)

        # Display the map
        st.write("### Interactive Map")
        st_folium(folium_map, width=900, height=600)

    else:
        st.error("Failed to process the uploaded .csv file.")
