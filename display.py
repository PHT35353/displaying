import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# Load the uploaded CSV and image
st.title("Interactive Map with Pipe and Landmark Information")

# Upload CSV file
csv_file = st.file_uploader("Upload the .csv file containing the pipe and landmark data", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load the CSV data
    data = pd.read_csv(csv_file)
    st.write("Uploaded Data:")
    st.dataframe(data)

    # Load the map screenshot
    screenshot = Image.open(screenshot_file)

    # Validate and convert the Coordinates column
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(isinstance(c, list) and len(c) == 2 for c in parsed):
                return parsed
        except:
            return None  # Return None if invalid
        return None

    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)

    # Filter out rows with invalid coordinates
    valid_data = data.dropna(subset=["Coordinates"])

    # Create Plotly figure
    fig = go.Figure()

    # Add the map screenshot as a background
    fig.add_layout_image(
        dict(
            source=screenshot,
            xref="x",
            yref="y",
            x=0, y=100,  # Adjust according to your map dimensions
            sizex=100,
            sizey=100,
            xanchor="left",
            yanchor="top",
            layer="below",
        )
    )

    # Add pipes (lines) to the figure
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if coords and row["Length (meters)"] > 0:  # Pipe
            x, y = zip(*coords)  # Separate x and y coordinates
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode="lines+markers+text",
                line=dict(color="blue", width=2),
                name=row["Name"],
                text=[row["Name"]] * len(x),
                hoverinfo="text"
            ))

    # Add landmarks (points) to the figure
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if coords and row["Length (meters)"] == 0:  # Landmark
            fig.add_trace(go.Scatter(
                x=[coords[0][0]], y=[coords[0][1]],
                mode="markers+text",
                marker=dict(color="black", size=10),
                name=row["Name"],
                text=row["Name"],
                hoverinfo="text"
            ))

    # Update layout
    fig.update_layout(
        title="Interactive Map with Pipes and Landmarks",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        dragmode="select",  # Allow selection of points
        margin=dict(l=0, r=0, t=0, b=0),
    )

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

    # Add a note if rows were skipped due to invalid coordinates
    invalid_rows = data[data["Coordinates"].isna()]
    if not invalid_rows.empty:
        st.warning(f"Skipped {len(invalid_rows)} rows due to invalid or missing coordinates.")
