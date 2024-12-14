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

    # Validate and clean the "Coordinates" column
    def validate_coordinates(coord):
        try:
            # Parse coordinates (e.g., from string to list)
            parsed = eval(coord) if isinstance(coord, str) else coord
            # Ensure it's a list of [x, y] or [[x1, y1], [x2, y2], ...]
            if isinstance(parsed, list) and all(
                isinstance(c, list) and len(c) == 2 and all(isinstance(i, (int, float)) for i in c) for c in parsed
            ):
                return parsed
        except:
            pass
        return None  # Return None for invalid entries

    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)

    # Filter out invalid rows
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
        if row["Length (meters)"] > 0:  # Pipe
            x, y = zip(*coords)  # Separate x and y coordinates
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color="blue", width=2),
                marker=dict(size=8),
                name=row["Name"],
                hovertemplate=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Length:</b> {row['Length (meters)']} meters<br>"
                    f"<b>Medium:</b> {row['Medium']}<br>"
                    f"<b>Coordinates:</b> {coords}"
                ),
            ))

    # Add landmarks (points) to the figure
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] == 0:  # Landmark
            fig.add_trace(go.Scatter(
                x=[coords[0][0]],
                y=[coords[0][1]],
                mode="markers+text",
                marker=dict(color="red", size=10),
                text=[f"{row['Name']}<br>{coords[0]}"],
                textposition="top right",
                name=row["Name"],
                hovertemplate=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Coordinates:</b> {coords[0]}"
                ),
            ))

    # Update layout
    fig.update_layout(
        title="Interactive Map with Pipes and Landmarks",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        dragmode="pan",  # Allow panning on the map
        margin=dict(l=0, r=0, t=30, b=0),
    )

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

    # Add a note if rows were skipped due to invalid coordinates
    invalid_rows = data[data["Coordinates"].isna()]
    if not invalid_rows.empty:
        st.warning(f"Skipped {len(invalid_rows)} rows due to invalid or missing coordinates.")
