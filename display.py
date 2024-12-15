import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# Title
st.title("Interactive Map with Pipes and Landmarks")

# Upload files
csv_file = st.file_uploader("Upload the .csv file containing the pipe and landmark data", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load data
    data = pd.read_csv(csv_file)
    st.write("Uploaded Data:")
    st.dataframe(data)

    # Load image
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
            pass
        return None

    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Initialize Plotly figure
    fig = go.Figure()

    # Add the map screenshot as a background
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

    # Adjust axes
    fig.update_xaxes(range=[0, screenshot_width], visible=False)
    fig.update_yaxes(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1)

    # Draw pipes (lines)
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] > 0:  # Pipe
            x, y = zip(*coords)
            fig.add_trace(go.Scatter(
                x=x,
                y=[screenshot_height - yi for yi in y],
                mode="lines+markers",
                line=dict(color="blue", width=2),
                marker=dict(size=8),
                name=f"{row['Name']} ({row['Medium']})",
                hovertemplate=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Length:</b> {row['Length (meters)']} meters<br>"
                    f"<b>Medium:</b> {row['Medium']}<br>"
                    f"<b>Coordinates:</b> {coords}"
                ),
            ))

    # Draw landmarks (points)
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] == 0:  # Landmark
            fig.add_trace(go.Scatter(
                x=[coords[0][0]],
                y=[screenshot_height - coords[0][1]],
                mode="markers+text",
                marker=dict(color="red", size=10),
                text=[f"{row['Name']} ({row['Medium']})"],
                textposition="top right",
                hovertemplate=(
                    f"<b>Name:</b> {row['Name']}<br>"
                    f"<b>Medium:</b> {row['Medium']}<br>"
                    f"<b>Coordinates:</b> {coords[0]}"
                ),
            ))

    # Update layout
    fig.update_layout(
        title="Pipes and Landmarks on Map",
        dragmode="pan",
        margin=dict(l=0, r=0, t=30, b=0),
    )

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

    # Warn about invalid rows
    invalid_rows = data[data["Coordinates"].isna()]
    if not invalid_rows.empty:
        st.warning(f"Skipped {len(invalid_rows)} rows due to invalid or missing coordinates.")
