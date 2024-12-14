import pandas as pd
import streamlit as st
import plotly.express as px
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

    # Convert coordinates from string to lists
    data["Coordinates"] = data["Coordinates"].apply(eval)

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
    for _, row in data.iterrows():
        coords = row["Coordinates"]
        x, y = zip(*coords)  # Separate x and y coordinates
        if row["Length (meters)"] > 0:  # Pipe
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode="lines+markers+text",
                line=dict(color="blue", width=2),
                name=row["Name"],
                text=[row["Name"]] * len(x),
                hoverinfo="text"
            ))

    # Add landmarks (points) to the figure
    for _, row in data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] == 0:  # Landmark
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

    # Interactive selection
    st.write("Click on the map to get more information about a pipe or landmark.")

    # Add interactivity to display info on click
    if "click_data" in st.session_state:
        selected_data = st.session_state["click_data"]
        st.write("Selected Element Info:")
        st.json(selected_data)
