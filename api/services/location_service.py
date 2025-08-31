import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MAPBOX_ACCESS_TOKEN")

import requests

def get_location_from_coords(lat, lon):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json?access_token={token}"
    res = requests.get(url)
    data = res.json()

    city, state, country = None, None, None

    for feature in data["features"]:
        if "place" in feature["place_type"]:
            city = feature["text"]
        if "region" in feature["place_type"]:
            state = feature["text"]
        if "country" in feature["place_type"]:
            country = feature["text"]

    if country == "United States" and city and state:
        return f"{city}, {state}"
    elif city and country:
        return f"{city}, {country}"
    return city or state or country or "Unknown"