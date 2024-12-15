import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import cv2

# Streamlit Title
st.title("Perfectly Aligned Map with Pipes and Landmarks")

# File Uploaders
csv_file = st.file_uploader("Upload the .csv file", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load Data
    data = pd.read_csv(csv_file)
    screenshot = Image.open(screenshot_file)
    screenshot_width, screenshot_height = screenshot.size

    # Coordinate Validation
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(isinstance(c, list) and len(c) == 2 for c in parsed):
                return parsed
        except:
            return None
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Step 1: Define Control Points for Homography
    st.info("Using 4 reference points to calibrate the map.")
    # Assume we know these control points for the map calibration
    geographic_points = np.array([
        [4.9044, 52.3676],  # Example: Longitude, Latitude (Top Left)
        [4.9050, 52.3676],  # Example: Top Right
        [4.9044, 52.3673],  # Bottom Left
        [4.9050, 52.3673]   # Bottom Right
    ], dtype=np.float32)

    # Corresponding Pixel Positions on the Map (manually measured or estimated)
    pixel_points = np.array([
        [100, 100],        # Top Left (x, y)
        [screenshot_width - 100, 100],  # Top Right
        [100, screenshot_height - 100], # Bottom Left
        [screenshot_width - 100, screenshot_height - 100]  # Bottom Right
    ], dtype=np.float32)

    # Compute Homography Matrix
    homography_matrix, _ = cv2.findHomography(geographic_points, pixel_points)

    # Step 2: Transform Coordinates Using Homography
    def transform_coordinates(coords):
        coords = np.array(coords, dtype=np.float32)
        coords = np.c_[coords, np.ones(len(coords))]  # Convert to homogeneous coordinates
        transformed_coords = np.dot(homography_matrix, coords.T).T
        transformed_coords = transformed_coords[:, :2] / transformed_coords[:, 2:]  # Normalize
        return transformed_coords

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

    # Step 3: Draw Pipes and Landmarks
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        transformed_coords = transform_coordinates(coords)

        if row["Length (meters)"] > 0:  # Draw Pipes
            x, y = transformed_coords[:, 0], screenshot_height - transformed_coords[:, 1]
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
            x, y = transformed_coords[0][0], screenshot_height - transformed_coords[0][1]
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
        title="Perfectly Aligned Map with Pipes and Landmarks",
        xaxis=dict(range=[0, screenshot_width], visible=False),
        yaxis=dict(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=30, b=0),
        dragmode="pan",
    )

    # Display the Map
    st.plotly_chart(fig, use_container_width=True)
