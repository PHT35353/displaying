import pandas as pd
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import folium_static

# Streamlit Title
st.title("Interactive Map with Pipes and Landmarks")

# Your Mapbox Token
mapbox_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# File Uploaders
csv_file = st.file_uploader("Upload the .csv file with coordinates", type=["csv"])

if csv_file:
    # Load CSV File
    data = pd.read_csv(csv_file)

    # Coordinate Validation Function (Improved)
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            # Ensure it's either a single coordinate or a list of coordinates
            if isinstance(parsed, list):
                if all(len(c) == 2 for c in parsed):  # Multiple coordinates (lines)
                    return parsed
                elif len(parsed) == 2:  # Single coordinate (landmark)
                    return [parsed]  # Wrap it in a list for uniformity
        except:
            return None  # Invalid coordinate
        return None

    # Apply Validation and Debug
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    st.write("Data After Coordinate Validation:")
    st.write(data)

    # Avoid Dropping Landmarks: Retain All Valid Rows
    valid_data = data.dropna(subset=["Coordinates"])

    # Initialize Map Centered at Mean Coordinates
    all_coords = [coord for row in valid_data["Coordinates"] for coord in row]
    avg_lat = sum(lat for _, lat in all_coords) / len(all_coords)
    avg_lon = sum(lon for lon, _ in all_coords) / len(all_coords)
    map_center = [avg_lat, avg_lon]

    # Use Mapbox Satellite Tiles
    tile_layer = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_token}"
    m = folium.Map(location=map_center, zoom_start=21, max_zoom=21, tiles=tile_layer, attr="Mapbox")

    # Add Pipes and Landmarks to the Map
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]

        # Pipes: Multiple Coordinates
        if len(coords) > 1:
            pipe_line = [(lat, lon) for lon, lat in coords]
            folium.PolyLine(
                pipe_line,
                color="blue",
                weight=3,
                popup=folium.Popup(
                    f"Name: {row['Name']}<br>"
                    f"Medium: {row.get('Medium', 'N/A')}<br>"
                    f"Length: {row.get('Length (meters)', 'N/A')} meters<br>"
                    f"Start: {pipe_line[0]}<br>"
                    f"End: {pipe_line[-1]}",
                    max_width=300
                )
            ).add_to(m)
        # Landmarks: Single Coordinate
        elif len(coords) == 1:
            landmark = coords[0]
            folium.Marker(
                location=(landmark[1], landmark[0]),  # Latitude, Longitude
                icon=folium.Icon(color="red", icon="info-sign"),
                popup=folium.Popup(
                    f"Name: {row['Name']}<br>"
                    f"Coordinates: ({landmark[1]}, {landmark[0]})",
                    max_width=300
                )
            ).add_to(m)

    # Add Fullscreen Plugin
    plugins.Fullscreen().add_to(m)

    # Display Map
    st.subheader("Interactive Map:")
    folium_static(m)
