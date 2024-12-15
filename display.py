import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import numpy as np
from scipy.spatial import distance

# Streamlit title
st.title("Accurately Scaled Map with Pipes and Landmarks")

# File uploaders
csv_file = st.file_uploader("Upload the .csv file containing pipe and landmark data", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load CSV and image
    data = pd.read_csv(csv_file)
    screenshot = Image.open(screenshot_file)
    screenshot_width, screenshot_height = screenshot.size

    # Coordinate validation
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

    # Function to rescale coordinates
    def rescale_coordinates(coords, img_width, img_height):
        x_min = min(c[0] for c in coords)
        y_min = min(c[1] for c in coords)
        x_max = max(c[0] for c in coords)
        y_max = max(c[1] for c in coords)
        x_range = x_max - x_min
        y_range = y_max - y_min

        return [
            [(img_width * (x - x_min) / x_range), img_height - (img_height * (y - y_min) / y_range)]
            for x, y in coords
        ]

    # Rescale all coordinates to match the image dimensions
    for _, row in valid_data.iterrows():
        row["Coordinates"] = rescale_coordinates(row["Coordinates"], screenshot_width, screenshot_height)

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

    # Add pipes (lines) and landmarks
    all_coords = []
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] > 0:  # Draw pipes (lines)
            x, y = zip(*coords)
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode="lines+markers",
                line=dict(color="blue", width=3),
                marker=dict(size=6),
                name=row['Name'],
                hoverinfo="text",
                hovertext=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Medium:</b> {row['Medium']}<br>"
                    f"<b>Coordinates:</b> {coords}"
                )
            ))
            all_coords.extend(coords)
        else:  # Approximate landmarks
            landmark_x, landmark_y = row["Coordinates"][0]
            closest_line_point = min(all_coords, key=lambda p: distance.euclidean((landmark_x, landmark_y), p))
            fig.add_trace(go.Scatter(
                x=[closest_line_point[0]],
                y=[closest_line_point[1]],
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

    # Adjust layout
    fig.update_layout(
        title="Interactive Scaled Map with Pipes and Landmarks",
        xaxis=dict(range=[0, screenshot_width], visible=False),
        yaxis=dict(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=30, b=0),
        dragmode="pan",
    )

    # Display the interactive map
    st.plotly_chart(fig, use_container_width=True)
