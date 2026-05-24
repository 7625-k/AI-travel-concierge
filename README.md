# ✈️ AI Travel Concierge

An advanced, interactive, and beautiful AI-powered travel assistant web application. It features a conversational AI companion, custom day-by-day itinerary planning, flight search, hotel suggestions, real-time geocoding, interactive maps, POI exploration, packing lists, and local search history.

Developed using **Streamlit**, **Groq (Llama 3)**, **OpenWeatherMap**, **Nominatim OpenStreetMap**, and **SQLite**.

---

# 🌐 Live Demo
https://ai-travel-conciergee.streamlit.app/

---

## 🌟 Key Features

The application is structured around a horizontal navigation system containing 10 distinct, customized workspaces:

1. **💬 Chat Assistant**: A conversational travel chatbot with glowing dialogue bubbles and quick suggestion prompts.
2. **📅 AI Trip Planner**: Generates personalized, day-by-day itineraries packaged into modern, glassmorphic collapsible boards.
3. **🛫 Flights**: Explores realistic flight options between origins and destinations.
4. **🎭 Mood & Vibe**: Suggests tailor-made travel destinations matching your current emotional mood or vibe.
5. **🏨 Hotels & Stays**: Recommends hotels matching specific destinations and budget tiers.
6. **🔍 Nearby Explorer**: Bounded map search that locates points of interest (Restaurants, Museums, Cafes, Shopping, Parks) around a destination.
7. **💰 Budget Calculator**: Adds up travel expense estimations.
8. **🗺️ Interactive Maps**: Renders custom maps with visual pins.
9. **🧳 Packing Assistant**: Automatically creates categorised packing lists based on trip length, trip type (e.g. adventure, business), and season.
10. **📜 Search History**: Keeps track of all past searches, itineraries, and maps stored in your local database.

---

## 🛠️ Tech Stack & Services

* **Frontend**: Streamlit, HTML5, and custom Vanilla CSS with custom animations and deep-space glowing UI.
* **LLM Engine**: Groq Client (`llama-3.3-70b-versatile`)
* **Database**: SQLite3 (Local persistence for user authentication, past searches, and generated itineraries)
* **APIs**:
  * **OpenWeatherMap**: Live weather information for destinations.
  * **Nominatim OpenStreetMap**: High-precision geocoding and location-bounded POI lookup.

---

## 📂 Project Structure

```text
├── src/
│   ├── agents/
│   │   └── travel_agent.py          # Core AI completion agents (hotels, packing, vibe)
│   ├── database/
│   │   └── db.py                    # SQLite schema migration, users, and search history tables
│   ├── itinerary/
│   │   └── itinerary_generator.py   # AI day-by-day itinerary planner generator
│   ├── tools/
│   │   └── travel_tools.py          # Geocoding, OpenWeatherMap, and Nominatim API interfaces
│   └── ui/
│       └── app.py                   # Main Streamlit web application (UI logic & styling)
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
```

---

## 🚀 Local Installation & Setup

### Prerequisites
* Python 3.10 or higher
* A Groq API Key (Free)
* An OpenWeatherMap API Key (Free)

### 1. Clone the repository
```bash
git clone https://github.com/7625-k/AI-travel-concierge.git
cd AI-travel-concierge
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory and paste your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
SERP_API_KEY=your_serp_api_key_here
```

### 5. Launch the application
```bash
streamlit run src/ui/app.py
```
The app will initialize database tables automatically and open at `http://localhost:8501`.

---

## ☁️ Deployment (Streamlit Community Cloud)

This app is optimized to run seamlessly on **Streamlit Community Cloud** (free and permanent hosting).

1. Push your project to your GitHub repository.
2. Sign in to [share.streamlit.io](https://share.streamlit.io) using your GitHub account.
3. Click **New app** and specify:
   * **Repository**: `7625-k/AI-travel-concierge`
   * **Branch**: `main`
   * **Main file path**: `src/ui/app.py`
4. Click **Advanced settings...** next to the deploy button.
5. In the **Secrets** text box, paste your TOML credentials:
   ```toml
   GROQ_API_KEY = "your_actual_groq_key"
   WEATHER_API_KEY = "your_actual_weather_key"
   SERP_API_KEY = "your_actual_serp_key"
   ```
6. Click **Save**, then click **Deploy**.
