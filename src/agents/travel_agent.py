import os
import re

from groq import Groq
from dotenv import load_dotenv

from src.tools.travel_tools import (
    get_weather,
    get_travel_tips
)

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def extract_city(text):

    text = re.sub(r"[^\w\s]", "", text)

    words = text.lower().split()

    keywords = ["in", "for", "to"]

    for keyword in keywords:

        if keyword in words:

            index = words.index(keyword)

            city = " ".join(words[index + 1:])

            return city.title()

    return "Paris"


def ask_agent(question):

    question_lower = question.lower()

    if "weather" in question_lower:

        city = extract_city(question)

        weather = get_weather(city)

        prompt = f"""
        User asked weather information.

        Weather:
        {weather}

        Give a friendly response.
        """

    elif "tip" in question_lower:

        destination = extract_city(question)

        tips = get_travel_tips(destination)

        prompt = f"""
        User wants travel tips.

        Tips:
        {tips}
        """

    else:

        prompt = question

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": "You are an AI travel concierge."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content


def get_hotel_recommendations(destination, budget_class):
    import json
    
    prompt = f"""
    You are an expert travel concierge.
    Generate a JSON list of 5 recommended hotels in {destination} that fit the budget class: '{budget_class}'.
    Each hotel must have:
    - "name": Hotel name
    - "price_range": Price range per night (in Indian Rupees, e.g. "₹3,500 - ₹5,000 per night" or "₹12,000 - ₹18,000 per night")
    - "rating": Float value out of 5 (e.g. 4.6)
    - "type": E.g., Luxury, Budget, Boutique, Heritage, Business, Resort
    - "highlights": A list of exactly 3 brief bullet points (e.g., ["Infinity Pool", "Ocean view", "Free shuttle"])
    - "description": A short 1-2 sentence description highlighting why travelers love it.

    Return ONLY a raw JSON array of objects. Do NOT wrap it in ```json ... ``` code blocks. Do not add any introductory or concluding text. Just return the valid JSON array starting with [ and ending with ].
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise JSON travel generator. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = completion.choices[0].message.content.strip()
        # Clean up any potential markdown wraps
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()
        
        return json.loads(response_text)
    except Exception as e:
        # Fallback list if JSON parsing or API fails
        return [
            {
                "name": f"Grand {destination} Hotel",
                "price_range": "₹5,000 - ₹8,000 per night",
                "rating": 4.5,
                "type": "Mid-Range / Premium",
                "highlights": ["Excellent Location", "Free High-Speed Wi-Fi", "Complimentary Breakfast"],
                "description": "A popular choice featuring modern amenities, comfortable rooms, and top-tier hospitality in the heart of the city."
            },
            {
                "name": f"{destination} Heritage Inn",
                "price_range": "₹3,000 - ₹5,000 per night",
                "rating": 4.2,
                "type": "Boutique / Heritage",
                "highlights": ["Local Architecture", "Rooftop Café", "Friendly Staff"],
                "description": "Charming stay rich with local cultural aesthetics, offering a cozy ambiance and scenic neighborhood views."
            },
            {
                "name": f"Sunrise {destination} Resort",
                "price_range": "₹8,000 - ₹12,000 per night",
                "rating": 4.7,
                "type": "Resort / Luxury",
                "highlights": ["Swimming Pool", "Spa & Wellness Center", "Panoramic Views"],
                "description": "A luxury resort experience with top-tier wellness facilities and spectacular views of the local surroundings."
            }
        ]


def get_flight_recommendations(origin, destination, departure_date, travel_class):
    import json
    
    prompt = f"""
    You are an expert travel concierge.
    Generate a JSON list of 5 realistic flight options from '{origin}' to '{destination}' departing on '{departure_date}' for travel class '{travel_class}'.
    Each flight must have:
    - "airline": Airline name (e.g. Emirates, Air India, Singapore Airlines, Lufthansa)
    - "flight_number": Flight code (e.g. EK-512, AI-302, LH-760)
    - "departure_time": Local departure time (e.g. "08:30 AM")
    - "arrival_time": Local arrival time (e.g. "02:15 PM")
    - "duration": Total travel duration (e.g. "5h 45m" or "12h 10m")
    - "layovers": Number of layovers and transit cities (e.g. "Non-stop" or "1 Stop (Doha)")
    - "price": Price range per traveler (in Indian Rupees, e.g. "₹22,500 - ₹28,000" or "₹45,000 - ₹52,000")
    - "class": The travel class (e.g. Economy, Premium Economy, Business, First Class)
    - "highlights": A list of exactly 3 brief amenities/highlights (e.g. ["Free Hot Meal", "USB Power Outlet", "30kg Checked Bag"])
    
    Return ONLY a raw JSON array of objects. Do NOT wrap it in ```json ... ``` code blocks. Do not add any introductory or concluding text. Just return the valid JSON array starting with [ and ending with ].
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise JSON travel generator. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()
        
        return json.loads(response_text)
    except Exception as e:
        # Fallback list if JSON parsing or API fails
        return [
            {
                "airline": "Air India",
                "flight_number": "AI-161",
                "departure_time": "02:45 AM",
                "arrival_time": "07:30 AM",
                "duration": "9h 15m",
                "layovers": "Non-stop",
                "price": "₹42,500 - ₹48,000",
                "class": travel_class,
                "highlights": ["Warm Meals Included", "2x 23kg Checked Bags", "Generous Legroom"]
            },
            {
                "airline": "Emirates",
                "flight_number": "EK-511",
                "departure_time": "10:30 AM",
                "arrival_time": "06:45 PM",
                "duration": "12h 45m",
                "layovers": "1 Stop (Dubai)",
                "price": "₹55,000 - ₹62,000",
                "class": travel_class,
                "highlights": ["Award-winning Entertainment", "Wi-Fi onboard", "30kg Checked Bag"]
            },
            {
                "airline": "IndiGo",
                "flight_number": "6E-45",
                "departure_time": "06:15 PM",
                "arrival_time": "03:20 AM",
                "duration": "13h 35m",
                "layovers": "1 Stop (Istanbul)",
                "price": "₹32,000 - ₹38,000",
                "class": travel_class,
                "highlights": ["Budget Friendly", "Buy-on-board Meals", "15kg Checked Bag"]
            }
        ]


def get_mood_suggestions(mood_query):
    import json
    
    prompt = f"""
    You are an expert travel concierge.
    Suggest 3 destinations that fit the user's emotional mood/vibe: '{mood_query}'.
    Each suggestion must have:
    - "name": Destination name (e.g. "Kerala Backwaters, India", "Prague, Czech Republic", "Bangkok, Thailand", "Bhutan (Paro)", "Kyoto, Japan")
    - "vibe_class": A short category/theme for the vibe matching the mood (e.g. "healing", "cinematic", "chaotic fun", "peaceful", "adventure")
    - "duration": Suggested trip duration (e.g. "3 days", "3-5 days")
    - "description": A short 2-3 sentence description explaining why this destination fits their specific mood.
    - "best_season": Recommended months/seasons to visit (e.g., "September to March")
    - "lat": Latitude coordinate as float (e.g. 9.4981)
    - "lon": Longitude coordinate as float (e.g. 76.3388)

    Return ONLY a raw JSON array of objects. Do NOT wrap it in ```json ... ``` code blocks. Do not add any introductory or concluding text. Just return the valid JSON array starting with [ and ending with ].
    """
    
    # Establish robust fallbacks for typical prompts or general fallback
    query_lower = mood_query.lower()
    
    # We will prioritize LLM but fallback locally if parsing or network fails.
    fallbacks = [
        {
            "name": "Kerala Backwaters, India",
            "vibe_class": "healing",
            "duration": "3-5 days",
            "description": "Slow down and restore your energy with a tranquil houseboat cruise along palm-fringed canals. The serene waters and Ayurvedic wellness treatments make it the ultimate healing retreat.",
            "best_season": "October to March",
            "lat": 9.4981,
            "lon": 76.3388
        },
        {
            "name": "Prague, Czech Republic",
            "vibe_class": "cinematic",
            "duration": "3-4 days",
            "description": "Wander through mist-shrouded gothic streets, historic stone bridges, and castles. Prague feels like stepping straight into a classic film set, perfect for a cinematic and romantic escape.",
            "best_season": "April to October",
            "lat": 50.0755,
            "lon": 14.4378
        },
        {
            "name": "Bangkok, Thailand",
            "vibe_class": "chaotic fun",
            "duration": "3 days",
            "description": "Dive into the electrifying energy of neon-lit night markets, vibrant street food scenes, and bustling tuk-tuks. Ideal for an exciting, fast-paced, and highly interactive adventure.",
            "best_season": "November to February",
            "lat": 13.7563,
            "lon": 100.5018
        }
    ]
    
    # Customize fallbacks based on keyword matches to make them feel highly responsive
    if "burn" in query_lower or "healing" in query_lower or "stress" in query_lower or "tired" in query_lower or "health" in query_lower or "heal" in query_lower:
        fallbacks = [
            {
                "name": "Kerala Backwaters, India",
                "vibe_class": "healing",
                "duration": "3-5 days",
                "description": "Slow down and restore your energy with a tranquil houseboat cruise along palm-fringed canals. The serene waters and Ayurvedic wellness treatments make it the ultimate healing retreat.",
                "best_season": "October to March",
                "lat": 9.4981,
                "lon": 76.3388
            },
            {
                "name": "Kyoto, Japan",
                "vibe_class": "peaceful healing",
                "duration": "4-5 days",
                "description": "Walk among tranquil bamboo groves, historic Zen temples, and pristine rock gardens. A meditative environment designed to calm a busy mind.",
                "best_season": "October to November, April to May",
                "lat": 35.0116,
                "lon": 135.7681
            },
            {
                "name": "Swiss Alps (Zermatt), Switzerland",
                "vibe_class": "alpine healing",
                "duration": "3-4 days",
                "description": "Inhale crisp mountain air, gaze at the majestic Matterhorn, and relax in thermal pools. The car-free village offers a silent refuge from modern burnout.",
                "best_season": "December to April, July to September",
                "lat": 46.0207,
                "lon": 7.7491
            }
        ]
    elif "disappear" in query_lower or "isolated" in query_lower or "remote" in query_lower or "3 days" in query_lower:
        fallbacks = [
            {
                "name": "Bhutan (Paro Valley)",
                "vibe_class": "isolated mystery",
                "duration": "3-5 days",
                "description": "Trek up to the iconic Tiger's Nest monastery perched on a sheer cliff. A majestic kingdom where gross national happiness is prioritized over commercial tourism.",
                "best_season": "October to December",
                "lat": 27.4287,
                "lon": 89.4164
            },
            {
                "name": "Lofoten Islands, Norway",
                "vibe_class": "remote wildness",
                "duration": "3-4 days",
                "description": "Disappear into dramatic fjords, towering peaks, and cozy red fisherman cabins. Perfect for disconnect under the Midnight Sun or the Northern Lights.",
                "best_season": "June to August, September to April",
                "lat": 68.1666,
                "lon": 13.7500
            },
            {
                "name": "Maldives (Private Atoll)",
                "vibe_class": "luxury escape",
                "duration": "3 days",
                "description": "Recline in an overwater villa surrounded by infinite turquoise waters. Ideal for complete isolation where your only schedule is the rise and fall of the tide.",
                "best_season": "November to April",
                "lat": 3.2028,
                "lon": 73.2207
            }
        ]
    elif "cinematic" in query_lower or "movie" in query_lower or "picturesque" in query_lower or "gothic" in query_lower:
        fallbacks = [
            {
                "name": "Prague, Czech Republic",
                "vibe_class": "cinematic gothic",
                "duration": "3-4 days",
                "description": "Wander through mist-shrouded gothic streets, historic stone bridges, and castles. Prague feels like stepping straight into a classic film set, perfect for a cinematic and romantic escape.",
                "best_season": "April to October",
                "lat": 50.0755,
                "lon": 14.4378
            },
            {
                "name": "Iceland (South Coast)",
                "vibe_class": "cinematic sci-fi",
                "duration": "4-5 days",
                "description": "Explore black sand beaches, thundering waterfalls, and massive glacier lagoons. Its otherworldly landscapes have served as the backdrop for numerous blockbuster movies.",
                "best_season": "June to August, September to March",
                "lat": 63.4194,
                "lon": -19.0060
            },
            {
                "name": "Kyoto, Japan",
                "vibe_class": "cinematic historic",
                "duration": "3-5 days",
                "description": "Capture the visual poetry of bright red Torii gates, traditional wooden teahouses, and cherry blossoms falling gracefully. A dream for storytellers and photographers.",
                "best_season": "April or October",
                "lat": 35.0116,
                "lon": 135.7681
            }
        ]
    elif "chaotic" in query_lower or "fun" in query_lower or "energy" in query_lower or "party" in query_lower or "wild" in query_lower:
        fallbacks = [
            {
                "name": "Bangkok, Thailand",
                "vibe_class": "chaotic fun",
                "duration": "3 days",
                "description": "Dive into the electrifying energy of neon-lit night markets, vibrant street food scenes, and bustling tuk-tuks. Ideal for an exciting, fast-paced, and highly interactive adventure.",
                "best_season": "November to February",
                "lat": 13.7563,
                "lon": 100.5018
            },
            {
                "name": "Las Vegas, USA",
                "vibe_class": "sensory overload",
                "duration": "3 days",
                "description": "Immerse yourself in spectacular world-class shows, towering themed casinos, and endless nightlife. A chaotic, high-stakes adult playground that never sleeps.",
                "best_season": "September to November, March to May",
                "lat": 36.1716,
                "lon": -115.1398
            },
            {
                "name": "Ibiza, Spain",
                "vibe_class": "electric escape",
                "duration": "3-4 days",
                "description": "Dance all night at world-famous beach clubs and rest during the day on gorgeous Mediterranean beaches. The perfect blend of party energy and coastal sunshine.",
                "best_season": "May to October",
                "lat": 38.9067,
                "lon": 1.4206
            }
        ]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise JSON travel generator. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()
        
        parsed = json.loads(response_text)
        if isinstance(parsed, list) and len(parsed) > 0:
            from src.tools.travel_tools import geocode_place
            for dest in parsed:
                name = dest.get("name")
                if name:
                    # Clean any trailing descriptions/parenthesis for better geocoding
                    clean_name = name.split("(")[0].strip()
                    lat_g, lon_g, _ = geocode_place(clean_name)
                    if lat_g is not None and lon_g is not None:
                        dest["lat"] = lat_g
                        dest["lon"] = lon_g
            return parsed
        return fallbacks
    except Exception as e:
        return fallbacks


def get_packing_list(destination, duration, trip_type, season):
    import json
    
    prompt = f"""
    You are an expert travel assistant.
    Generate a comprehensive packing list for a trip to '{destination}' for a duration of {duration} days.
    The trip type is '{trip_type}' and the season/weather is '{season}'.
    
    Structure the recommendations into a JSON object with exactly the following categories:
    - "Clothing": A list of items to pack (with specific clothing suited to '{trip_type}' and '{season}', e.g., thermal wear, swimwear, hiking boots, formal suit, etc.).
    - "Toiletries": List of personal care and hygiene products.
    - "Electronics": Devices, chargers, adapters suitable for '{destination}'.
    - "Documents": Passports, visas, booking confirmations, insurance, etc.
    - "Essentials": Other general items like medicines, sunblock, umbrella, water bottle, backpack, etc.
    
    Format:
    Each item in the list must be a string. Give at least 4-6 items per category. Make it highly relevant to the destination, trip type, and weather.
    
    Return ONLY a raw JSON object. Do NOT wrap it in ```json ... ``` code blocks. Do not add any introductory or concluding text. Just return the valid JSON object starting with {{ and ending with }}.
    """
    
    # Heuristic Fallback
    fallbacks = {
        "Clothing": ["Comfortable walking shoes", "T-shirts & tops", "Light jacket / sweater", "Underwear & socks"],
        "Toiletries": ["Toothbrush & toothpaste", "Shampoo & conditioner", "Soap / body wash", "Deodorant", "Travel towel"],
        "Electronics": ["Smartphone & charger", "Power bank", "Universal travel adapter", "Headphones"],
        "Documents": ["Passport / ID", "Flight & hotel booking confirmations", "Travel insurance printout", "Credit/debit cards & cash"],
        "Essentials": ["Refillable water bottle", "First-aid kit (painkillers, band-aids)", "Tissues / wet wipes", "Small daypack / backpack"]
    }
    
    # Tailor fallback based on inputs
    try:
        duration_days = int(duration)
    except:
        duration_days = 3
        
    # Weather modifications
    if "winter" in season.lower() or "cold" in season.lower():
        fallbacks["Clothing"].extend(["Thermal underwear", "Heavy winter coat / parka", "Gloves, scarf & beanie", "Warm socks"])
        fallbacks["Essentials"].extend(["Lip balm (for dry lips)", "Hand warmers"])
    elif "summer" in season.lower() or "warm" in season.lower() or "beach" in trip_type.lower():
        fallbacks["Clothing"].extend(["Swimwear / shorts", "Sunglasses", "Sun hat / cap", "Sandals / flip-flops"])
        fallbacks["Essentials"].extend(["Sunscreen (SPF 50+)", "Insect repellent"])
    elif "monsoon" in season.lower() or "rainy" in season.lower():
        fallbacks["Clothing"].extend(["Waterproof jacket / raincoat", "Waterproof shoes / boots"])
        fallbacks["Essentials"].extend(["Compact umbrella", "Waterproof dry bag"])
        
    # Trip type modifications
    if "adventure" in trip_type.lower():
        fallbacks["Clothing"].extend(["Sturdy hiking boots", "Moisture-wicking athletic wear", "Quick-dry pants"])
        fallbacks["Essentials"].extend(["Flashlight / headlamp", "Multi-tool", "Energy bars", "Hydration bladder"])
    elif "business" in trip_type.lower():
        fallbacks["Clothing"].extend(["Formal suit / blazer", "Dress shirts & trousers", "Ironed dress shoes"])
        fallbacks["Electronics"].extend(["Laptop & charger", "Notebook & pen", "Business cards"])
    elif "romantic" in trip_type.lower():
        fallbacks["Clothing"].extend(["Elegant evening wear / dress", "Nice shoes"])
        fallbacks["Essentials"].extend(["Scented lotion", "Small gifts / surprises"])
    elif "winter sports" in trip_type.lower():
        fallbacks["Clothing"].extend(["Ski jacket & snow pants", "Thermal base layers", "Ski socks & goggles"])
        fallbacks["Essentials"].extend(["Ski/snowboard gear pass", "Moisturizer / cold cream"])
        
    # Add destination-specific essentials
    if "india" in destination.lower():
        fallbacks["Essentials"].extend(["Hand sanitizer", "Mosquito repellent", "Modest clothing options (for temples)"])
    elif "europe" in destination.lower() or any(x in destination.lower() for x in ["paris", "rome", "london", "swiss", "france", "italy", "germany", "spain"]):
        fallbacks["Electronics"].extend(["Europlug adapter (Type C/E/F)"])
        fallbacks["Documents"].extend(["Schengen Visa (if required)"])
    elif "japan" in destination.lower() or "tokyo" in destination.lower():
        fallbacks["Clothing"].extend(["Slip-on shoes (easy to remove at temples/homes)"])
        fallbacks["Essentials"].extend(["Coin purse (Japan uses many coins)", "Suica/Pasmo card app"])
        
    # Remove duplicates
    for cat in fallbacks:
        fallbacks[cat] = list(dict.fromkeys(fallbacks[cat]))

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise JSON travel assistant. Output raw JSON only matching the requested schema."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()
        
        parsed = json.loads(response_text)
        # Ensure categories exist
        for cat in ["Clothing", "Toiletries", "Electronics", "Documents", "Essentials"]:
            if cat not in parsed or not isinstance(parsed[cat], list):
                parsed[cat] = fallbacks[cat]
        return parsed
    except Exception as e:
        return fallbacks


def analyze_review_sentiment(review_text):
    import json
    
    prompt = f"""
    You are an expert travel review analyst.
    Analyze the sentiment of the following travel/hotel review:
    ---
    {review_text}
    ---
    
    Provide a detailed sentiment analysis returning ONLY a JSON object containing:
    - "sentiment": "Positive", "Negative", or "Neutral".
    - "score": A confidence score or strength percentage (integer between 0 and 100).
    - "summary": A brief 1-2 sentence summary of the main points in the review.
    - "pros": A list of positive aspects mentioned (maximum 4 points, e.g. ["Friendly staff", "Great central location"]). If none, return empty list.
    - "cons": A list of negative aspects or complaints mentioned (maximum 4 points, e.g. ["Noisy street view", "Slow check-in"]). If none, return empty list.
    - "tags": A list of key categories/topics discussed in the review (e.g. ["Service", "Cleanliness", "Food", "Location", "Value", "Rooms"]).
    
    Return ONLY a raw JSON object. Do NOT wrap it in ```json ... ``` code blocks. Do not add any introductory or concluding text. Just return the valid JSON object starting with {{ and ending with }}.
    """
    
    # Keyword-based fallback
    lower_text = review_text.lower()
    
    # List of positive and negative keywords
    pos_words = ["good", "great", "excellent", "fantastic", "amazing", "beautiful", "wonderful", "love", "friendly", "clean", "perfect", "awesome", "helpful", "delicious", "nice", "comfortable", "spotless", "welcoming"]
    neg_words = ["bad", "worst", "terrible", "horrible", "dirty", "noisy", "disappointed", "poor", "slow", "loud", "rude", "overpriced", "expensive", "hate", "small", "broken", "uncomfortable", "smell", "annoyed", "failed"]
    
    pos_count = sum(lower_text.count(word) for word in pos_words)
    neg_count = sum(lower_text.count(word) for word in neg_words)
    
    # Determine sentiment and score
    if pos_count > neg_count:
        sentiment = "Positive"
        diff = pos_count - neg_count
        score = min(50 + diff * 10, 95)
    elif neg_count > pos_count:
        sentiment = "Negative"
        diff = neg_count - pos_count
        score = min(50 + diff * 10, 95)
    else:
        sentiment = "Neutral"
        score = 50
        
    # Heuristic pros and cons
    pros = []
    cons = []
    tags = []
    
    # Heuristic tagging
    if any(x in lower_text for x in ["staff", "service", "help", "desk", "people", "reception", "manager"]):
        tags.append("Service")
        if "friendly" in lower_text or "helpful" in lower_text or "nice" in lower_text:
            pros.append("Friendly and helpful staff")
        elif "rude" in lower_text or "slow" in lower_text:
            cons.append("Poor or slow staff service")
            
    if any(x in lower_text for x in ["clean", "dirty", "spotless", "smell", "sheet", "hygiene"]):
        tags.append("Cleanliness")
        if "clean" in lower_text or "spotless" in lower_text:
            pros.append("Clean and well-maintained rooms")
        elif "dirty" in lower_text or "smell" in lower_text:
            cons.append("Room cleanliness issues")
            
    if any(x in lower_text for x in ["location", "near", "close", "center", "metro", "station", "walk"]):
        tags.append("Location")
        if "great" in lower_text or "good" in lower_text or "perfect" in lower_text or "close" in lower_text:
            pros.append("Great, convenient location")
        elif "far" in lower_text or "noisy" in lower_text:
            cons.append("Noisy or inconvenient location")
            
    if any(x in lower_text for x in ["food", "breakfast", "dinner", "eat", "restaurant", "delicious", "buffet"]):
        tags.append("Food")
        if "delicious" in lower_text or "great" in lower_text or "good" in lower_text:
            pros.append("Delicious food/breakfast options")
        elif "limited" in lower_text or "cold" in lower_text or "bad" in lower_text:
            cons.append("Limited or poor breakfast options")
            
    if any(x in lower_text for x in ["price", "cost", "value", "expensive", "cheap", "worth"]):
        tags.append("Value")
        if "worth" in lower_text or "reasonable" in lower_text or "cheap" in lower_text:
            pros.append("Good value for money")
        elif "expensive" in lower_text or "overpriced" in lower_text:
            cons.append("Expensive or overpriced stay")
            
    if not tags:
        tags = ["General"]
    if not pros and sentiment == "Positive":
        pros = ["Nice stay overall"]
    if not cons and sentiment == "Negative":
        cons = ["Some operational issues occurred"]
        
    summary = review_text[:100] + "..." if len(review_text) > 100 else review_text
    
    fallbacks = {
        "sentiment": sentiment,
        "score": score,
        "summary": f"Review sentiment analysis: Heuristically classified as {sentiment} based on text cues.",
        "pros": pros,
        "cons": cons,
        "tags": tags
    }
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise JSON review analyst. Output raw JSON only matching the requested schema."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "", 1)
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()
        
        parsed = json.loads(response_text)
        # Validate keys
        for key in ["sentiment", "score", "summary", "pros", "cons", "tags"]:
            if key not in parsed:
                parsed[key] = fallbacks[key]
        return parsed
    except Exception as e:
        return fallbacks