import pandas as pd
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import folium_static

# Streamlit Title
st.title("Pipes and Landmarks on an Interactive Map")

# File Uploaders
csv_file = st.file_uploader("Upload the .csv file with coordinates", type=["csv"])

if csv_file:
    # Load CSV File
    data = pd.read_csv(csv_file)

    # Coordinate Validation Function
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(len(c) == 2 for c in parsed):
                return parsed
        except:
            return None
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Initialize Map Centered at Mean Coordinates
    all_coords = [coord for row in valid_data["Coordinates"] for coord in row]
    avg_lat = sum(lat for _, lat in all_coords) / len(all_coords)
    avg_lon = sum(lon for lon, _ in all_coords) / len(all_coords)
    map_center = [avg_lat, avg_lon]

    m = folium.Map(location=map_center, zoom_start=15)

    # Add Pipes and Landmarks to the Map
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]

        if row["Length (meters)"] > 0:  # Pipes
            # Add Pipe as a Polyline
            pipe_line = [(lat, lon) for lon, lat in coords]  # Convert to (lat, lon)
            folium.PolyLine(
                pipe_line,
                color="blue",
                weight=3,
                popup=folium.Popup(
                    f"Name: {row['Name']}<br>Medium: {row['Medium']}<br>Length: {row['Length (meters)']} meters",
                    max_width=300
                )
            ).add_to(m)
        else:  # Landmarks
            # Add Landmark as a Marker
            landmark = coords[0]
            folium.Marker(
                location=(landmark[1], landmark[0]),  # (lat, lon)
                icon=folium.Icon(color="red", icon="info-sign"),
                popup=folium.Popup(
                    f"Name: {row['Name']}<br>Coordinates: ({landmark[1]}, {landmark[0]})",
                    max_width=300
                )
            ).add_to(m)

    # Add Fullscreen Plugin for Better Viewing
    plugins.Fullscreen().add_to(m)

    # Display Map
    folium_static(m)
