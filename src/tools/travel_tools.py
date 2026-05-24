import requests
import os

from dotenv import load_dotenv

load_dotenv()


def get_weather(city):

    api_key = os.getenv("WEATHER_API_KEY")

    url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    return response.json()


def get_travel_tips(destination):

    tips = {
        "Paris": "Visit Eiffel Tower early morning.",
        "Tokyo": "Use metro pass for travel.",
        "Dubai": "Best season is November to March."
    }

    return tips.get(
        destination,
        f"Research local customs before visiting {destination}"
    )


def geocode_place(query, allow_correction=True):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "AI-Travel-Concierge-App/1.0"
    }

    try:

        response = requests.get(url, params=params, headers=headers, timeout=10)

        data = response.json()

        if data and len(data) > 0:

            lat = float(data[0]["lat"])

            lon = float(data[0]["lon"])

            display_name = data[0]["display_name"]

            # Use the first element of display_name as short label

            short_name = display_name.split(",")[0]

            return lat, lon, short_name

    except Exception:

        pass

    # Fallback to Weather API geocoding if Nominatim fails

    try:

        weather_data = get_weather(query)

        if weather_data and "coord" in weather_data:

            lat = weather_data["coord"]["lat"]

            lon = weather_data["coord"]["lon"]

            return lat, lon, query.title()

    except Exception:

        pass

    # LLM-based spelling and formatting correction fallback if both geocoders fail
    if allow_correction:
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                client = Groq(api_key=api_key)
                prompt = f"""
                You are a precise spelling and location correction assistant.
                The user entered a location search query that might contain typos, misspellings, or formatting issues: '{query}'.
                Correct the spelling of any city, country, region, landmark, or street name.
                Return ONLY the corrected, clean location query (e.g. if input is 'electronic city,benguluru' return 'electronic city, bengaluru') without any surrounding quotes, punctuation, preamble, or explanation.
                If the query is already correct, return it exactly as-is.
                """
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a precise location spelling corrector. Output the corrected location query only, no extra text."},
                        {"role": "user", "content": prompt}
                    ]
                )
                corrected = completion.choices[0].message.content.strip().strip("'\"")
                if corrected and corrected.lower() != query.lower():
                    # Retry geocoding with the corrected query and prevent infinite recursion
                    return geocode_place(corrected, allow_correction=False)
        except Exception:
            pass

    return None, None, None


def get_nearby_places(location_query, category_query):
    # Mapping friendly category names to single robust search queries for viewbox bounded search
    cat_mapping_single = {
        "🍽️ Restaurants & Dining": "restaurant",
        "🏛️ Tourist Attractions": "museum",
        "☕ Cafes & Bars": "cafe",
        "🛍️ Shopping & Malls": "mall",
        "🌳 Parks & Nature": "park"
    }
    
    cat_mapping_fallback = {
        "🍽️ Restaurants & Dining": "restaurant dining food",
        "🏛️ Tourist Attractions": "tourist attraction monument museum historic",
        "☕ Cafes & Bars": "cafe bar coffee pub",
        "🛍️ Shopping & Malls": "mall shopping supermarket marketplace",
        "🌳 Parks & Nature": "park garden nature forest"
    }
    
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "AI-Travel-Concierge-App/1.0"
    }
    
    # Try to geocode the center first
    lat_c, lon_c, _ = geocode_place(location_query)
    
    if lat_c is not None and lon_c is not None:
        osm_query = cat_mapping_single.get(category_query, "museum")
        # Construct bounding box (viewbox) roughly 10km around center
        # left, top, right, bottom => min_lon, max_lat, max_lon, min_lat
        min_lon = lon_c - 0.1
        max_lon = lon_c + 0.1
        min_lat = lat_c - 0.1
        max_lat = lat_c + 0.1
        viewbox = f"{min_lon},{max_lat},{max_lon},{min_lat}"
        
        params = {
            "q": osm_query,
            "viewbox": viewbox,
            "bounded": 1,
            "format": "json",
            "limit": 10
        }
    else:
        osm_query = cat_mapping_fallback.get(category_query, "tourist attraction")
        params = {
            "q": f"{osm_query} in {location_query}",
            "format": "json",
            "limit": 10
        }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            results = response.json()
            formatted_results = []
            for item in results:
                display_name = item.get("display_name", "")
                parts = display_name.split(",")
                # Form clean title and subtext
                title = parts[0].strip()
                subtitle = ", ".join([p.strip() for p in parts[1:4]]) if len(parts) > 1 else ""
                
                formatted_results.append({
                    "name": title,
                    "address": subtitle or display_name,
                    "lat": float(item["lat"]),
                    "lon": float(item["lon"]),
                    "type": item.get("type", "POI").replace("_", " ").title()
                })
            return formatted_results
    except Exception as e:
        print("Error fetching nearby places:", e)
    return []
