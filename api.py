from fastapi import FastAPI, UploadFile, File
import pandas as pd
from typing import Dict, List

app = FastAPI()

# Endpoint to fetch the map tiles or settings
@app.get("/map-settings")
async def get_map_settings():
    # Mock example: Return settings for Mapbox
    return {
        "mapbox_access_token": "pk.eyJ1IjoiY29kZW1hcCIsImEiOiJja2xsNzh2aTQwN3J1MnBvODFlOTlscXBkIn0.OEoHgUzO5DPkF-XUmSn_9A",
        "center_coordinates": [52.3676, 4.9041],  # Example: Amsterdam
        "zoom_level": 15,
    }


# Endpoint to process uploaded .csv file
@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)) -> Dict[str, List[Dict]]:
    # Read the .csv file
    try:
        contents = await file.read()
        df = pd.read_csv(pd.compat.StringIO(contents.decode("utf-8")))

        # Validate the coordinates column
        def validate_coordinates(coord):
            try:
                parsed = eval(coord) if isinstance(coord, str) else coord
                if isinstance(parsed, list) and all(
                    isinstance(c, list) and len(c) == 2 and all(isinstance(i, (int, float)) for i in c) for c in parsed
                ):
                    return parsed
            except:
                return None

        df["Coordinates"] = df["Coordinates"].apply(validate_coordinates)
        valid_data = df.dropna(subset=["Coordinates"])

        # Convert the dataframe into a structured dictionary
        result = valid_data.to_dict(orient="records")
        return {"status": "success", "data": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}
