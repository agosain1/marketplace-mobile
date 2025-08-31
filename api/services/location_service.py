import os
from dotenv import load_dotenv
import re

load_dotenv()

token = os.getenv("MAPBOX_ACCESS_TOKEN")

import requests
from api.database import get_db_cursor

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

def search_us_zipcode_db(query):
    """
    Search for US location in local database by zipcode or city name
    """
    with get_db_cursor() as cur:
        # Check if query is a zipcode (5 digits)
        if re.match(r'^\d{5}$', query):
            cur.execute(
                "SELECT zipcode, city, state, state_code, latitude, longitude FROM us_zipcodes WHERE zipcode = %s LIMIT 1",
                (query,)
            )
        else:
            # Search by city name (case insensitive)
            cur.execute(
                """
                SELECT zipcode, city, state, state_code, latitude, longitude 
                FROM us_zipcodes 
                WHERE LOWER(city) = LOWER(%s) 
                ORDER BY zipcode 
                LIMIT 1
                """,
                (query,)
            )
        
        result = cur.fetchone()
        if result:
            return {
                "latitude": float(result["latitude"]),
                "longitude": float(result["longitude"]),
                "place_name": f"{result['city']}, {result['state_code']}"
            }
    
    return None

def search_location(query):
    """
    Search for a location by city, zipcode, or address and return coordinates
    First checks US zipcode database, then falls back to Mapbox API
    """
    # First try local US zipcode database
    us_result = search_us_zipcode_db(query)
    if us_result:
        return us_result
    
    # Fall back to Mapbox API for international locations or unmatched queries
    """url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={token}&limit=1"
    res = requests.get(url)
    
    if res.status_code != 200:
        return None
        
    data = res.json()
    
    if data["features"] and len(data["features"]) > 0:
        feature = data["features"][0]
        lon, lat = feature["center"]
        place_name = feature["place_name"]
        
        return {
            "latitude": lat,
            "longitude": lon,
            "place_name": place_name
        }"""
    
    return None