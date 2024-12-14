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

    # Get the dimensions of the screenshot
    screenshot_width, screenshot_height = screenshot.size

    # Validate and clean the "Coordinates" column
    def validate_coordinates(coord):
        try:
            parsed = eval(coord) if isinstance(coord, str) else coord
            if isinstance(parsed, list) and all(
                isinstance(c, list) and len(c) == 2 and all(isinstance(i, (int, float)) for i in c) for c in parsed
            ):
                return parsed
        except:
            pass
        return None  # Return None for invalid entries

    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Create Plotly figure
    fig = go.Figure()

    # Add the map screenshot as a background
    fig.add_layout_image(
        dict(
            source=screenshot,
            xref="x",
            yref="y",
            x=0,
            y=screenshot_height,  # Set the y-axis to match the image height
            sizex=screenshot_width,  # Match the image width
            sizey=screenshot_height,  # Match the image height
            xanchor="left",
            yanchor="top",
            layer="below",
        )
    )

    # Adjust axis ranges to fit the image
    fig.update_xaxes(range=[0, screenshot_width], visible=False)
    fig.update_yaxes(range=[0, screenshot_height], visible=False, scaleanchor="x", scaleratio=1)

    # Add pipes (lines) to the figure
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] > 0:  # Pipe
            x, y = zip(*coords)  # Separate x and y coordinates
            fig.add_trace(go.Scatter(
                x=x,
                y=[screenshot_height - yi for yi in y],  # Invert y-coordinates for Plotly's coordinate system
                mode="lines+markers+text",
                line=dict(color="blue", width=2),
                marker=dict(size=8),
                name=row["Name"],
                textposition="middle center",
                text=[f"{row['Name']}<br>Length: {row['Length (meters)']}m<br>Medium: {row['Medium']}"],
                hoverinfo="text",
            ))

    # Add landmarks (points) to the figure
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] == 0:  # Landmark
            fig.add_trace(go.Scatter(
                x=[coords[0][0]],
                y=[screenshot_height - coords[0][1]],  # Invert y-coordinates
                mode="markers+text",
                marker=dict(color="red", size=10),
                text=[f"{row['Name']}<br>Coordinates: {coords[0]}"],
                textposition="top right",
                name=row["Name"],
                hoverinfo="text",
            ))

    # Update layout
    fig.update_layout(
        title="Interactive Map with Pipes and Landmarks",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        dragmode=False,  # Disable dragging
        margin=dict(l=0, r=0, t=30, b=0),
    )

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

    # Add a note if rows were skipped due to invalid coordinates
    invalid_rows = data[data["Coordinates"].isna()]
    if not invalid_rows.empty:
        st.warning(f"Skipped {len(invalid_rows)} rows due to invalid or missing coordinates.")
