import pandas as pd
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import folium_static

# Streamlit Title
st.title("Interactive Map with Pipes, Landmarks, and Extreme Zoom")

# Your Mapbox Token
mapbox_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

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

    # Clean and Validate Data
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Separate Pipes and Landmarks
    pipes = valid_data.dropna(subset=["Length (meters)"])
    landmarks = valid_data[valid_data["Length (meters)"].isna()]  # Explicitly filter landmarks

    # Debugging Outputs
    st.write("Pipes Data:")
    st.write(pipes)
    st.write("Landmarks Data:")
    st.write(landmarks)

    # Initialize Map Centered at Mean Coordinates
    all_coords = [coord for row in valid_data["Coordinates"] for coord in row]
    avg_lat = sum(lat for _, lat in all_coords) / len(all_coords)
    avg_lon = sum(lon for lon, _ in all_coords) / len(all_coords)
    map_center = [avg_lat, avg_lon]

    # Use Mapbox Satellite Tiles for 3D View
    tile_layer = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_token}"
    m = folium.Map(location=map_center, zoom_start=21, max_zoom=21, tiles=tile_layer, attr="Mapbox")

    # Add Pipes to the Map
    for _, row in pipes.iterrows():
        coords = row["Coordinates"]
        pipe_line = [(lat, lon) for lon, lat in coords]  # Convert to (lat, lon)
        folium.PolyLine(
            pipe_line,
            color="blue",
            weight=3,
            popup=folium.Popup(
                f"Name: {row['Name']}<br>"
                f"Medium: {row['Medium']}<br>"
                f"Length: {row['Length (meters)']} meters<br>"
                f"Start: {pipe_line[0]}<br>"
                f"End: {pipe_line[-1]}",
                max_width=300
            )
        ).add_to(m)

    # Add Landmarks to the Map
    for _, row in landmarks.iterrows():
        coords = row["Coordinates"][0]  # Use first coordinate for landmarks
        folium.Marker(
            location=(coords[1], coords[0]),  # Latitude, Longitude
            icon=folium.Icon(color="red", icon="info-sign"),
            popup=folium.Popup(
                f"Name: {row['Name']}<br>"
                f"Coordinates: ({coords[1]}, {coords[0]})",
                max_width=300
            )
        ).add_to(m)

    # Add Fullscreen Plugin for Better Viewing
    plugins.Fullscreen().add_to(m)

    # Display Map
    st.subheader("Interactive Map:")
    folium_static(m)
