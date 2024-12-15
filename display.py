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

    # Step 1: Detect Reference Points (Bounding Box Detection)
    def detect_reference_points(image):
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        reference_pixels = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 50 and h > 50:  # Filter small detections
                reference_pixels.append([x, y])
        return np.array(reference_pixels[:4], dtype=np.float32)

    # Automatically detected pixel points
    detected_pixels = detect_reference_points(screenshot)
    if len(detected_pixels) < 4:
        st.error("Could not detect enough reference points automatically. Please ensure the map is clear.")
        st.stop()

    # Geographic points from the CSV (assume four corner points exist)
    geographic_points = np.array([
        valid_data["Coordinates"].iloc[0][0],  # Top-left
        valid_data["Coordinates"].iloc[0][-1],  # Top-right
        valid_data["Coordinates"].iloc[-1][0],  # Bottom-left
        valid_data["Coordinates"].iloc[-1][-1]  # Bottom-right
    ], dtype=np.float32)

    # Step 2: Compute Homography Matrix
    homography_matrix, _ = cv2.findHomography(geographic_points, detected_pixels)

    # Step 3: Transform Coordinates Using Homography
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

    # Step 4: Draw Pipes and Landmarks
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
