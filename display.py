import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st

# Streamlit App
st.title("Map Display Tool")
st.markdown("Upload the `.csv` file and visualize the drawn features on the map.")

# File uploader
uploaded_file = st.file_uploader("Upload your .csv file", type=["csv"])

if uploaded_file is not None:
    # Load the CSV data
    data = pd.read_csv(uploaded_file)
    st.dataframe(data)

    # Load map screenshot
    map_image = Image.open("map_screenshot.png")  # Replace with your screenshot path
    
    # Create the map overlay
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(map_image, extent=[0, 100, 0, 100])  # Adjust extent to match your coordinates
    
    # Plot features
    for idx, row in data.iterrows():
        coordinates = eval(row['Coordinates'])  # Assuming coordinates are stored as stringified lists
        x, y = zip(*coordinates)
        
        if row['Length (meters)'] > 0:  # Pipe
            ax.plot(x, y, label=row['Name'], linestyle="--")
        else:  # Landmark or polygon
            ax.scatter(x, y, label=row['Name'], s=50)

        # Add annotations
        ax.text(x[0], y[0], f"{row['Name']} ({row['Medium']}, {row['Material']})", fontsize=8, color='blue')

    # Customize plot
    ax.legend()
    ax.set_title("Map with Features")
    ax.axis("off")
    
    # Display the map
    st.pyplot(fig)
