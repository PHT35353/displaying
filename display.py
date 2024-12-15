import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# Streamlit title
st.title("Interactive Map with Pipes and Landmarks")

# File uploaders
csv_file = st.file_uploader("Upload the .csv file containing pipe and landmark data", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load CSV and image
    data = pd.read_csv(csv_file)
    screenshot = Image.open(screenshot_file)
    screenshot_width, screenshot_height = screenshot.size

    # Validate coordinates
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(
                isinstance(c, list) and len(c) == 2 and all(isinstance(i, (int, float)) for i in c) for c in parsed
            ):
                return parsed
        except:
            return None
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Initialize Plotly figure
    fig = go.Figure()

    # Add background map screenshot
    fig.add_layout_image(
        dict(
            source=screenshot,
            xref="x",
            yref="y",
            x=0,
            y=screenshot_height,
            sizex=screenshot_width,
            sizey=screenshot_height,
            xanchor="left",
            yanchor="top",
            layer="below",
        )
    )

    # Add lines and points
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] > 0:  # Draw pipes (lines)
            x, y = zip(*coords)
            y = [screenshot_height - yi for yi in y]  # Flip y-coordinates
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode="lines+markers",
                line=dict(color="blue", width=2),
                marker=dict(size=8),
                name=row['Name'],
                hoverinfo="text",
                hovertext=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Medium:</b> {row['Medium']}<br>"
                    f"<b>Coordinates:</b> {coords}"
                )
            ))
        elif row["Length (meters)"] == 0:  # Draw landmarks (points)
            x, y = coords[0]
            y = screenshot_height - y  # Flip y-coordinate
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                marker=dict(color="red", size=10),
                text=[row['Name']],
                textposition="top right",
                hoverinfo="text",
                hovertext=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Coordinates:</b> {coords[0]}"
                )
            ))

    # Adjust layout
    fig.update_layout(
        title="Interactive Map with Pipes and Landmarks",
        xaxis=dict(range=[0, screenshot_width], visible=False),
        yaxis=dict(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=30, b=0),
        dragmode="pan",
    )

    # Display the interactive map
    st.plotly_chart(fig, use_container_width=True)
