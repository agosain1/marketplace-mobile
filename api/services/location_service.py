import os
from dotenv import load_dotenv
import re
import math

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
            if ',' in query:
                # city, state
                query = query.split(',')
                city = query[0].strip()
                state = query[1].strip()
                # state abbreviation
                if len(state) < 3:
                    cur.execute(
                        """
                        SELECT zipcode, city, state, state_code, latitude, longitude 
                        FROM us_zipcodes 
                        WHERE LOWER(city) = LOWER(%s) AND LOWER(state_code) = LOWER(%s) 
                        ORDER BY zipcode DESC LIMIT 1
                        """,
                        (city, state)
                    )
                # full state name
                else:
                    cur.execute(
                        """
                        SELECT zipcode, city, state, state_code, latitude, longitude
                        FROM us_zipcodes
                        WHERE LOWER(city) = LOWER(%s) AND LOWER(state) = LOWER(%s)
                        ORDER BY zipcode DESC LIMIT 1
                        """,
                        (city, state)
                    )
            else:
                cur.execute(
                    """
                    SELECT zipcode, city, state, state_code, latitude, longitude
                    FROM us_zipcodes
                    WHERE LOWER(city) = LOWER(%s)
                    ORDER BY zipcode DESC LIMIT 1
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
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={token}&limit=1"
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
        }
    
    return None

def search_location_suggestions(query, limit=5):
    """
    Get location suggestions for autocomplete from US zipcode database
    """
    if not query or len(query) < 2:
        return []
    
    with get_db_cursor() as cur:
        suggestions = []
        
        # Search for zipcodes starting with query
        if query.isdigit():
            cur.execute(
                """
                SELECT DISTINCT zipcode, city, state_code, latitude, longitude 
                FROM us_zipcodes 
                WHERE zipcode LIKE %s 
                ORDER BY zipcode 
                LIMIT %s
                """,
                (f"{query}%", limit)
            )
            results = cur.fetchall()
            for result in results:
                suggestions.append({
                    "type": "zipcode",
                    "display": f"{result['zipcode']} - {result['city']}, {result['state_code']}",
                    "value": result['zipcode'],
                    "latitude": float(result['latitude']),
                    "longitude": float(result['longitude']),
                    "place_name": f"{result['city']}, {result['state_code']}"
                })
        else:
            # Search for cities starting with query - get one representative location per city/state
            cur.execute(
                """
                SELECT DISTINCT ON (city, state_code) city, state_code, latitude, longitude 
                FROM us_zipcodes 
                WHERE LOWER(city) LIKE LOWER(%s) 
                ORDER BY city, state_code, zipcode 
                LIMIT %s
                """,
                (f"{query}%", limit)
            )
            results = cur.fetchall()
            for result in results:
                suggestions.append({
                    "type": "city",
                    "display": f"{result['city']}, {result['state_code']}",
                    "value": f"{result['city']}, {result['state_code']}",
                    "latitude": float(result['latitude']),
                    "longitude": float(result['longitude']),
                    "place_name": f"{result['city']}, {result['state_code']}"
                })
    
    return suggestions

def get_bounding_box_corners(lat, lon, distance_miles):
    """
    Returns 4 corner coordinates (NE, NW, SE, SW) of a square
    bounding box `distance_miles` away from the center in all directions.
    """
    # Approximate radius of Earth in miles
    R = 3958.8

    # Convert distance in miles to angular distance in radians
    delta_lat = distance_miles / R
    delta_lon = distance_miles / (R * math.cos(math.radians(lat)))

    # Convert angular distances to degrees
    delta_lat_deg = math.degrees(delta_lat)
    delta_lon_deg = math.degrees(delta_lon)

    # Compute corners
    northeast = (lat + delta_lat_deg, lon + delta_lon_deg)
    northwest = (lat + delta_lat_deg, lon - delta_lon_deg)
    southeast = (lat - delta_lat_deg, lon + delta_lon_deg)
    southwest = (lat - delta_lat_deg, lon - delta_lon_deg)

    return {
        "northeast": northeast,
        "northwest": northwest,
        "southeast": southeast,
        "southwest": southwest
    }

# {'northeast': (37.144730169528856, -120.81877819392193), 'northwest': (37.144730169528856, -121.18122180607807), 'southeast': (36.855269830471144, -120.81877819392193), 'southwest': (36.855269830471144, -121.18122180607807)}