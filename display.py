import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import numpy as np

# Streamlit Title
st.title("Auto-Aligned Map with Pipes and Landmarks (Fixed Scaling)")

# File Uploaders
csv_file = st.file_uploader("Upload the .csv file", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load CSV and Image
    data = pd.read_csv(csv_file)
    screenshot = Image.open(screenshot_file)
    screenshot_width, screenshot_height = screenshot.size

    # Coordinate Validation
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(len(c) == 2 for c in parsed):
                return parsed
        except:
            return None
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Step 1: Normalize Coordinates to Image Bounds
    all_coords = [coord for row in valid_data["Coordinates"] for coord in row]
    x_min, x_max = min(x for x, _ in all_coords), max(x for x, _ in all_coords)
    y_min, y_max = min(y for _, y in all_coords), max(y for _, y in all_coords)

    def normalize_coordinates(coords):
        """Scale and normalize coordinates to fit the image dimensions."""
        x_scaled = [(x - x_min) / (x_max - x_min) * screenshot_width for x, _ in coords]
        y_scaled = [(1 - (y - y_min) / (y_max - y_min)) * screenshot_height for _, y in coords]  # Flip y-axis
        return list(zip(x_scaled, y_scaled))

    # Initialize Plotly Figure
    fig = go.Figure()

    # Add Screenshot as Background
    fig.add_layout_image(
        dict(
            source=screenshot,
            xref="x", yref="y",
            x=0, y=screenshot_height,
            sizex=screenshot_width, sizey=screenshot_height,
            xanchor="left", yanchor="top", layer="below"
        )
    )

    # Step 2: Draw Pipes and Landmarks
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        scaled_coords = normalize_coordinates(coords)

        if row["Length (meters)"] > 0:  # Draw Pipes
            x, y = zip(*scaled_coords)
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode="lines+markers",
                line=dict(color="blue", width=3),
                marker=dict(size=6),
                name=row["Name"],
                hoverinfo="text",
                hovertext=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Medium:</b> {row['Medium']}<br>"
                    f"<b>Coordinates:</b> {row['Coordinates']}"
                )
            ))
        else:  # Draw Landmarks
            x, y = scaled_coords[0]
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                marker=dict(color="red", size=10),
                text=[row['Name']],
                textposition="top right",
                hoverinfo="text",
                hovertext=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Coordinates:</b> {row['Coordinates'][0]}"
                )
            ))

    # Layout Adjustments
    fig.update_layout(
        title="Auto-Aligned Map with Pipes and Landmarks",
        xaxis=dict(range=[0, screenshot_width], visible=False),
        yaxis=dict(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=30, b=0),
        dragmode="pan",
    )

    # Display the Map
    st.plotly_chart(fig, use_container_width=True)
