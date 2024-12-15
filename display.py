import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import cv2

# Streamlit Title
st.title("Auto-Aligned Map with Pipes and Landmarks Using Feature Detection")

# File Uploaders
csv_file = st.file_uploader("Upload the .csv file", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load Data
    data = pd.read_csv(csv_file)
    screenshot = Image.open(screenshot_file)
    screenshot = np.array(screenshot)  # Convert to NumPy array
    screenshot_height, screenshot_width = screenshot.shape[:2]

    # Validate Coordinates
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(len(c) == 2 for c in parsed):
                return parsed
        except:
            return None
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Step 1: ORB Feature Detection
    def detect_keypoints(image):
        orb = cv2.ORB_create(500)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        return keypoints, descriptors

    # Step 2: Homography Using Keypoints
    def find_homography(screenshot, coords):
        keypoints_screenshot, descriptors_screenshot = detect_keypoints(screenshot)
        # Simulate feature detection for geographic coordinates
        keypoints_geo = np.array(coords, dtype=np.float32)

        # Map ORB keypoints to pixel locations
        keypoints_pixels = np.array([kp.pt for kp in keypoints_screenshot[:len(coords)]], dtype=np.float32)

        if len(keypoints_geo) >= 4 and len(keypoints_pixels) >= 4:
            homography_matrix, _ = cv2.findHomography(keypoints_geo, keypoints_pixels, cv2.RANSAC, 5.0)
            return homography_matrix
        else:
            st.error("Not enough keypoints detected to compute homography.")
            st.stop()

    # Step 3: Transform Coordinates
    def transform_coordinates(coords, matrix):
        coords = np.array(coords, dtype=np.float32)
        coords = np.c_[coords, np.ones(len(coords))]
        transformed_coords = np.dot(matrix, coords.T).T
        transformed_coords = transformed_coords[:, :2] / transformed_coords[:, 2:]
        return transformed_coords

    # Combine all coordinates into a single list for homography
    all_geo_coords = []
    for _, row in valid_data.iterrows():
        all_geo_coords.extend(row["Coordinates"])

    # Compute homography
    homography_matrix = find_homography(screenshot, all_geo_coords)

    # Initialize Plotly Figure
    fig = go.Figure()

    # Add Screenshot as Background
    fig.add_layout_image(
        dict(
            source=Image.fromarray(screenshot),
            xref="x", yref="y",
            x=0, y=screenshot_height,
            sizex=screenshot_width, sizey=screenshot_height,
            xanchor="left", yanchor="top", layer="below"
        )
    )

    # Step 4: Draw Pipes and Landmarks
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        transformed_coords = transform_coordinates(coords, homography_matrix)

        if row["Length (meters)"] > 0:  # Draw Pipes
            x, y = transformed_coords[:, 0], transformed_coords[:, 1]
            fig.add_trace(go.Scatter(
                x=x, y=[screenshot_height - yi for yi in y],
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
        title="Auto-Aligned Map with Pipes and Landmarks",
        xaxis=dict(range=[0, screenshot_width], visible=False),
        yaxis=dict(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=30, b=0),
        dragmode="pan",
    )

    # Display the Map
    st.plotly_chart(fig, use_container_width=True)
