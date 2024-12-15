import pandas as pd
import cv2
import numpy as np
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

# Streamlit title
st.title("Annotated Map with Pipes and Landmarks")

# File uploaders
csv_file = st.file_uploader("Upload the .csv file", type=["csv"])
screenshot_file = st.file_uploader("Upload the map screenshot", type=["png", "jpg", "jpeg"])

if csv_file and screenshot_file:
    # Load CSV and screenshot
    data = pd.read_csv(csv_file)
    screenshot = Image.open(screenshot_file)
    screenshot = np.array(screenshot)  # Convert to NumPy array for OpenCV processing
    screenshot_height, screenshot_width = screenshot.shape[:2]

    # Coordinate validation function
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

    # Validate coordinates and filter valid data
    data["Coordinates"] = data["Coordinates"].apply(validate_coordinates)
    valid_data = data.dropna(subset=["Coordinates"])

    # Draw on the screenshot using OpenCV
    annotated_image = screenshot.copy()
    for _, row in valid_data.iterrows():
        coords = row["Coordinates"]
        if row["Length (meters)"] > 0:  # Draw pipes (lines)
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                cv2.line(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)  # Red lines
                cv2.putText(
                    annotated_image,
                    f"{row['Name']} ({row['Medium']})",
                    (int((x1 + x2) / 2), int((y1 + y2) / 2)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
        elif row["Length (meters)"] == 0:  # Draw landmarks (points)
            x, y = coords[0]
            cv2.circle(annotated_image, (int(x), int(y)), 8, (255, 0, 0), -1)  # Blue circles
            cv2.putText(
                annotated_image,
                f"{row['Name']} ({row['Medium']})",
                (int(x) + 10, int(y) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

    # Display the annotated image
    st.image(annotated_image, caption="Annotated Map with Pipes and Landmarks", use_column_width=True)

    # Save the annotated image
    output_path = "/mnt/data/annotated_map.png"
    cv2.imwrite(output_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    st.success(f"Annotated map saved successfully: {output_path}")
