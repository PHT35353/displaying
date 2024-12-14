import pandas as pd
import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium  # Import the streamlit-folium wrapper
import ast  # To safely parse coordinates

# Streamlit app title
st.title("Satellite Map with Pipe and Landmark Drawings")

# File upload for the .csv file
csv_file = st.file_uploader("Upload the .csv file containing the pipe and landmark data", type=["csv"])

if csv_file:
    # Load the CSV data
    data = pd.read_csv(csv_file)

    # Display the uploaded data
    st.write("Uploaded Data:")
    st.dataframe(data)

    # Validate and convert the coordinates column
    def validate_coordinates(coord):
        try:
            # Safely parse string representation of list to Python list
            parsed = ast.literal_eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(
                isinstance(c, list) and len(c) == 2 and all(isinstance(i, (int, float)) for i in c) for c in parsed
            ):
                return parsed
        except:
            pass
        return None  # Return None for invalid entries

    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Initialize a folium map (satellite view)
    # Center the map based on the first valid coordinate or default to a location
    initial_coords = valid_data["Coordinates"].iloc[0][0] if not valid_data.empty else [0, 0]
    folium_map = folium.Map(
        location=initial_coords,
        zoom_start=15,
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
    )

    # Add a marker cluster for landmarks
    marker_cluster = MarkerCluster().add_to(folium_map)

    # Add pipes (polylines) and landmarks (markers) to the map
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        name = row["Name"]
        if row["Length (meters)"] > 0:  # It's a pipe
            # Add a polyline for the pipe
            popup_content = f"""
            <b>Name:</b> {name}<br>
            <b>Length:</b> {row["Length (meters)"]} meters<br>
            <b>Medium:</b> {row["Medium"]}<br>
            <b>Coordinates:</b> {coords}
            """
            folium.PolyLine(
                locations=coords,
                color="blue",
                weight=3,
                tooltip=name,
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(folium_map)
        else:  # It's a landmark
            # Add a marker for the landmark
            popup_content = f"""
            <b>Name:</b> {name}<br>
            <b>Coordinates:</b> {coords[0]}
            """
            folium.Marker(
                location=coords[0],
                icon=folium.Icon(color="red", icon="info-sign"),
                tooltip=name,
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(marker_cluster)

    # Display the map in Streamlit using streamlit-folium
    st.write("### Interactive Satellite Map")
    st_folium(folium_map, width=700, height=500)
