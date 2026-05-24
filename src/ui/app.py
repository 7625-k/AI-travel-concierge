import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="AI Travel Concierge",
    page_icon="✈️",
    layout="wide"
)

import sys
import os
# Insert the project root directory at the beginning of the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import re
from streamlit_folium import st_folium

from src.agents.travel_agent import (
    ask_agent,
    get_hotel_recommendations,
    get_flight_recommendations,
    get_mood_suggestions,
    get_packing_list
)
from src.itinerary.itinerary_generator import (
    generate_itinerary
)
from src.itinerary.pdf_generator import (
    generate_itinerary_pdf
)
from src.budget.budget_calculator import (
    calculate_budget
)
from src.maps.maps import (
    create_map,
    create_multi_marker_map,
    create_mood_map,
    create_hotel_map
)
from src.tools.travel_tools import (
    get_nearby_places
)
from src.database.db import (
    create_database,
    save_search,
    get_recent_searches,
    create_user,
    verify_user,
    user_exists
)
import streamlit.components.v1 as components

# Initialize database tables
create_database()

# Inject Custom Modern CSS
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 75%, #020617 100%) !important;
        color: #F8FAFC !important;
    }
    
    /* Main Dashboard Layout optimization to fit screen */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 96% !important;
    }
    
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stAppViewBlockContainer"] > div > [data-testid="stVerticalBlock"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #020617;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 4px;
        border: 1px solid #334155;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6366F1;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
    }
    
    /* Hide Default Headers and Footers completely to prevent empty header space */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
    }
    
    /* Keyframe Animations */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-5px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    @keyframes pulse-glow {
        0% { box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.2), 0 0 0 0 rgba(99, 102, 241, 0.4); }
        50% { box-shadow: 0 8px 32px 12px rgba(99, 102, 241, 0.3), 0 0 0 8px rgba(99, 102, 241, 0); }
        100% { box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.2), 0 0 0 0 rgba(99, 102, 241, 0); }
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #070a13 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    .sidebar-title {
        margin-top: 10px !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
    }
    .sidebar-user-info {
        color: #94A3B8 !important;
        font-size: 0.9rem !important;
    }
    .sidebar-divider {
        height: 1px !important;
        background-color: #334155 !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Premium Main Header */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 28px;
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        margin-top: 0rem !important;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.08);
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
    }
    .header-user-status {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.9rem;
        background: rgba(255, 255, 255, 0.04);
        padding: 7px 16px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
    }
    .pulse-indicator {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    /* Card Container */
    .card-container {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 26px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    .card-container:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
        box-shadow: 0 15px 35px -10px rgba(99, 102, 241, 0.1), 0 10px 30px -10px rgba(0, 0, 0, 0.4);
    }
    .highlight-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.18);
        backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 26px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.1);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    .highlight-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(99, 102, 241, 0.35) !important;
        box-shadow: 0 15px 35px -5px rgba(99, 102, 241, 0.2);
    }
    
    /* Tab Navigation styling */
    div[data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6) !important;
        padding: 6px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
    }
    div[data-baseweb="tab-list"] button {
        background-color: transparent !important;
        color: #94A3B8 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }
    div[data-baseweb="tab-list"] button:hover {
        color: #F8FAFC !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }
    
    /* Custom Navigation Pills styling matching st.tabs look and feel */
    .st-key-navigation_pills {
        margin-bottom: 2rem !important;
    }
    
    .st-key-navigation_pills div[data-testid="stPillsStack"],
    .st-key-navigation_pills > div {
        gap: 8px !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
        padding: 6px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(12px) !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    /* Hide scrollbars on chrome/safari */
    .st-key-navigation_pills div[data-testid="stPillsStack"]::-webkit-scrollbar,
    .st-key-navigation_pills > div::-webkit-scrollbar {
        display: none !important;
    }
    
    .st-key-navigation_pills button {
        background-color: transparent !important;
        color: #94A3B8 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: nowrap !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }
    
    .st-key-navigation_pills button:hover {
        color: #F8FAFC !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    .st-key-navigation_pills button[kind="pillsActive"],
    .st-key-navigation_pills button[data-testid="stBaseButton-pillsActive"],
    .st-key-navigation_pills button[aria-pressed="true"],
    .st-key-navigation_pills button[aria-selected="true"],
    .st-key-navigation_pills button[aria-checked="true"],
    .st-key-navigation_pills button[data-pressed="true"],
    .st-key-navigation_pills button[data-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        font-weight: 700 !important;
    }
    

    /* Buttons Custom styling */
    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100%;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
        background: linear-gradient(135deg, #818CF8 0%, #6366F1 100%) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    div.stButton > button:active, div.stFormSubmitButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Inputs Styling */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #F8FAFC !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease !important;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {
        border-color: #818CF8 !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.25) !important;
        background-color: rgba(30, 41, 59, 0.8) !important;
    }
    
    /* Label styling */
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #E2E8F0 !important;
        letter-spacing: 0.01em;
        margin-bottom: 8px !important;
    }
    
    /* Dropdown/Select Styling */
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
    }
    
    /* Chat bubbles styling (Aligned speech) */
    div[data-testid="stChatMessage"] {
        background-color: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(10px);
        margin-bottom: 16px !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stChatMessage"]:hover {
        transform: translateY(-1px) !important;
    }
    div[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(79, 70, 229, 0.18) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 16px 16px 4px 16px !important;
        margin-left: 15% !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.08) !important;
    }
    div[data-testid="stChatMessageAssistant"] {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(124, 58, 237, 0.12) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 16px 16px 16px 4px !important;
        margin-right: 15% !important;
        box-shadow: 0 6px 18px rgba(139, 92, 246, 0.06) !important;
    }
    
    /* Suggestion pills container overrides */
    .suggestion-pills div.stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #94A3B8 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 6px 16px !important;
        font-size: 0.85rem !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    .suggestion-pills div.stButton > button:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #818CF8 !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Chat input textarea */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 10px !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15), 0 0 15px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Slider Customization */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #6366F1 !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 0 8px rgba(99, 102, 241, 0.6) !important;
    }
    div[data-testid="stSlider"] [class*="StyledTrack"] {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    div[data-testid="stSlider"] div[data-testid="stSliderTickBar"] + div {
        background: linear-gradient(90deg, #6366F1, #8b5cf6) !important;
    }
    
    /* Accordion / Expanders */
    div[data-testid="stExpander"] {
        background-color: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
        transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(99, 102, 241, 0.25) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.08);
    }
    div[data-testid="stExpander"] > details {
        border: none !important;
        background-color: transparent !important;
    }
    div[data-testid="stExpander"] > details > summary {
        background-color: rgba(30, 41, 59, 0.2) !important;
        color: #F8FAFC !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 14px 18px !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stExpander"] > details > summary:hover {
        background-color: rgba(99, 102, 241, 0.1) !important;
        color: #818CF8 !important;
    }
    
    /* Metric Card styling */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(8px) !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.12);
    }
    
    /* Budget allocation bar styling */
    .budget-bar-container {
        background-color: rgba(15, 23, 42, 0.6);
        border-radius: 10px;
        height: 22px;
        width: 100%;
        margin-top: 10px;
        margin-bottom: 20px;
        overflow: hidden;
        display: flex;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .budget-bar-hotel {
        background: linear-gradient(90deg, #6366F1, #818CF8);
        height: 100%;
        transition: width 0.3s ease;
    }
    .budget-bar-food {
        background: linear-gradient(90deg, #10B981, #34D399);
        height: 100%;
        transition: width 0.3s ease;
    }
    .budget-bar-transport {
        background: linear-gradient(90deg, #F59E0B, #FBBF24);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* Metric container typography override */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 750 !important;
        color: #F8FAFC !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8 !important;
    }
    
    /* rounded borders for folium map */
    iframe[title="streamlit_folium.st_folium"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Hotel Stay Card Premium styling */
    .hotel-card {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
    }
    .hotel-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15), 0 8px 24px rgba(0,0,0,0.3);
    }
    .hotel-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 8px;
    }
    .hotel-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .hotel-rating {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .hotel-price {
        font-size: 0.95rem;
        font-weight: 600;
        color: #818CF8;
        margin-bottom: 12px;
    }
    .hotel-desc {
        font-size: 0.85rem;
        color: #94A3B8;
        line-height: 1.5;
        margin-bottom: 16px;
        flex-grow: 1;
    }
    .hotel-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 16px;
    }
    .hotel-tag {
        font-size: 0.75rem;
        background: rgba(255, 255, 255, 0.04);
        color: #CBD5E1;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    /* Flight Card Premium styling */
    .flight-card {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
    }
    .flight-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15), 0 8px 24px rgba(0,0,0,0.3);
    }
    .flight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .flight-airline {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .flight-number {
        font-size: 0.75rem;
        background: rgba(255, 255, 255, 0.08);
        color: #94A3B8;
        padding: 2px 8px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .flight-price {
        font-size: 1.1rem;
        font-weight: 700;
        color: #10B981;
    }
    .flight-route-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.02);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.03);
        margin-bottom: 15px;
    }
    .flight-station {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .flight-time {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .flight-city {
        font-size: 0.8rem;
        color: #94A3B8;
    }
    .flight-path-viz {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 0 20px;
        position: relative;
    }
    .flight-line {
        width: 100%;
        height: 2px;
        background: dashed rgba(255, 255, 255, 0.15);
        position: relative;
    }
    .flight-icon-path {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #818CF8;
        font-size: 1rem;
    }
    .flight-duration {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 4px;
        text-align: center;
    }
    .flight-layovers {
        font-size: 0.75rem;
        color: #F59E0B;
        margin-top: 2px;
        text-align: center;
    }
    
    /* POI Card Styling for Nearby Explorer */
    .poi-card {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }
    .poi-card:hover {
        background: rgba(30, 41, 59, 0.5);
        border-color: rgba(99, 102, 241, 0.2);
        transform: translateX(2px);
    }
    .poi-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0 0 4px 0;
    }
    .poi-addr {
        font-size: 0.8rem;
        color: #94A3B8;
        margin: 0;
        line-height: 1.4;
    }
    .poi-type {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #10B981;
        background: rgba(16, 185, 129, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid rgba(16, 185, 129, 0.15);
    }
    iframe[title="streamlit_folium.st_folium"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Mood Card Premium Styling */
    .mood-card {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
    }
    .mood-card:hover {
        transform: translateY(-4px);
        border-color: rgba(168, 85, 247, 0.4);
        box-shadow: 0 12px 30px rgba(168, 85, 247, 0.2), 0 8px 24px rgba(0,0,0,0.3);
    }
    .mood-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .mood-vibe-tag {
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(168, 85, 247, 0.15);
        color: #E9D5FF;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(168, 85, 247, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .mood-meta {
        display: flex;
        gap: 15px;
        font-size: 0.85rem;
        color: #94A3B8;
        margin-bottom: 12px;
    }
    .mood-meta-item {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .mood-description {
        font-size: 0.95rem;
        color: #E2E8F0;
        line-height: 1.5;
    }
    .packing-category-header {
        background: rgba(30, 27, 75, 0.4) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
    }
    .packing-category-title {
        margin: 0 0 10px 0 !important;
        color: #818CF8 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    
    /* Premium Chat Assistant Bubbles UI/UX */
    [data-testid="stChatMessage"]:has(.user-msg-container) {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(79, 70, 229, 0.25) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 20px 20px 4px 20px !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.08) !important;
        margin-left: 15% !important;
        margin-bottom: 16px !important;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stChatMessage"]:has(.user-msg-container):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2), 0 0 10px rgba(99, 102, 241, 0.1) !important;
        border-color: rgba(99, 102, 241, 0.45) !important;
    }
    
    [data-testid="stChatMessage"]:has(.assistant-msg-container) {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.55) 0%, rgba(15, 23, 42, 0.65) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px 20px 20px 4px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
        margin-right: 15% !important;
        margin-bottom: 16px !important;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stChatMessage"]:has(.assistant-msg-container):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 10px rgba(168, 85, 247, 0.1) !important;
        border-color: rgba(168, 85, 247, 0.3) !important;
    }
    
    /* Premium input and form selectors focus glows */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] {
        background-color: rgba(2, 6, 23, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #F8FAFC !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stTextInput"] input:focus, 
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-baseweb="select"]:focus-within {
        border-color: #818CF8 !important;
        box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.18), 0 0 20px rgba(99, 102, 241, 0.1) !important;
        background-color: rgba(15, 23, 42, 0.65) !important;
    }
    
    /* Style Chat Input Area */
    [data-testid="stChatInput"] {
        border-radius: 18px !important;
        background-color: rgba(8, 11, 20, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(16px) !important;
        padding: 6px !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #F8FAFC !important;
        border: none !important;
        font-size: 0.96rem !important;
    }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #6366F1 0%, #a855f7 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2) !important;
    }
    [data-testid="stChatInput"] button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.4) !important;
    }

    /* Premium Expander UI/UX for Trip Planner Day-by-Day Itineraries */
    div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.35) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(99, 102, 241, 0.25) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08), 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stExpander"] > details {
        border: none !important;
        background: transparent !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 700 !important;
        color: #F8FAFC !important;
        padding: 14px 20px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        transition: background 0.3s ease !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background: rgba(255, 255, 255, 0.06) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        padding: 20px !important;
        color: #E2E8F0 !important;
        line-height: 1.65 !important;
        font-size: 0.96rem !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)




# Initialize session state for user session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "needs_scroll_to_top" not in st.session_state:
    st.session_state.needs_scroll_to_top = False
if "message_to_speak" not in st.session_state:
    st.session_state.message_to_speak = None
if "navigation_pills" not in st.session_state:
    st.session_state.navigation_pills = "💬 Chat Assistant"

# Require login to access app content
if not st.session_state.logged_in:
    import textwrap
    # Render page marker and background glowing orbs for absolute premium depth effect
    st.markdown(textwrap.dedent("""
        <div id='login-page-marker'></div>
        <div class="login-bg-glow glow-orb-1"></div>
        <div class="login-bg-glow glow-orb-2"></div>
    """), unsafe_allow_html=True)
    
    # Inject Premium Login UI Styles
    st.markdown(textwrap.dedent("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
            
            /* Apply premium typography globally to login page */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) [data-testid="stAppViewBlockContainer"] * {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            }

            /* Premium Background Gradient for the Entire Login Page */
            div[data-testid="stAppViewContainer"]:has(#login-page-marker) {
                background-color: #080a10 !important;
                background-image: radial-gradient(circle at 50% 50%, #121829 0%, #06080d 100%) !important;
            }
            
            /* Hide Default Streamlit Header/Footer Elements for Standalone SaaS Experience */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) header, 
            [data-testid="stAppViewContainer"]:has(#login-page-marker) footer, 
            [data-testid="stAppViewContainer"]:has(#login-page-marker) [data-testid="stHeader"], 
            [data-testid="stAppViewContainer"]:has(#login-page-marker) [data-testid="stToolbar"] {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                padding: 0 !important;
            }

            /* Ambient Floating Glowing Orbs with Mixed Gradients */
            .login-bg-glow {
                position: fixed;
                border-radius: 50%;
                filter: blur(130px);
                z-index: 0;
                pointer-events: none;
                opacity: 0.35;
                animation: orb-float 25s ease-in-out infinite alternate;
            }
            .glow-orb-1 {
                top: 15%;
                left: 25%;
                width: 380px;
                height: 380px;
                background: radial-gradient(circle at 30% 30%, rgba(99, 102, 241, 0.45) 0%, rgba(236, 72, 153, 0.18) 50%, rgba(99, 102, 241, 0) 100%) !important;
            }
            .glow-orb-2 {
                bottom: 15%;
                right: 25%;
                width: 440px;
                height: 440px;
                background: radial-gradient(circle at 70% 70%, rgba(168, 85, 247, 0.45) 0%, rgba(59, 130, 246, 0.18) 50%, rgba(168, 85, 247, 0) 100%) !important;
                animation-delay: -6s;
            }
            @keyframes orb-float {
                0% { transform: translate(0, 0) scale(1); }
                100% { transform: translate(70px, 50px) scale(1.15); }
            }

            /* Force parent containers to center layout both horizontally and vertically */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) [data-testid="stAppViewBlockContainer"] {
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                padding: 0 !important;
                min-height: 95vh !important;
            }

            [data-testid="stAppViewContainer"]:has(#login-page-marker) [data-testid="stAppViewBlockContainer"] div[data-testid="stVerticalBlock"] {
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stHorizontalBlock"] {
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
                display: flex !important;
            }

            /* Style the second column on the login page as the main card container with glassy gradients */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stHorizontalBlock"] > div:nth-of-type(2),
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-of-type(2),
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-of-type(2),
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stHorizontalBlock"] div[class*="stColumn"]:nth-of-type(2),
            [data-testid="stAppViewContainer"]:has(#login-page-marker) .stHorizontalBlock div[data-testid="stColumn"]:nth-of-type(2) {
                background: linear-gradient(135deg, rgba(16, 22, 38, 0.72) 0%, rgba(8, 11, 18, 0.85) 100%) !important;
                backdrop-filter: blur(30px) !important;
                border: 1px solid rgba(129, 140, 248, 0.12) !important;
                border-radius: 24px !important;
                padding: 45px 45px 38px 45px !important;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75), 
                            0 0 40px rgba(99, 102, 241, 0.08),
                            0 0 80px rgba(168, 85, 247, 0.04),
                            inset 0 1px 1px rgba(255, 255, 255, 0.12) !important;
                max-width: 480px !important;
                width: 100% !important;
                margin: 0 auto !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                z-index: 10 !important;
                transition: border-color 0.4s ease, box-shadow 0.4s ease !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stHorizontalBlock"] > div:nth-of-type(2):hover {
                border-color: rgba(168, 85, 247, 0.35) !important;
                box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), 
                            0 0 50px rgba(99, 102, 241, 0.22),
                            0 0 100px rgba(168, 85, 247, 0.15),
                            inset 0 1px 1px rgba(255, 255, 255, 0.18) !important;
            }

            /* Remove default tab borders/shadows */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stTab"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }
            
            /* Modern Segmented Capsule Tab Selection Control */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-baseweb="tab-list"] {
                background-color: rgba(2, 6, 23, 0.55) !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                padding: 5px !important;
                border-radius: 16px !important;
                margin: 0 auto 1.5rem auto !important;
                justify-content: center !important;
                gap: 8px !important;
                max-width: 380px !important;
                backdrop-filter: blur(10px);
                width: 100% !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-baseweb="tab-list"] button {
                flex: 1 !important;
                background-color: transparent !important;
                color: #94A3B8 !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 10px 20px !important;
                font-weight: 600 !important;
                font-size: 0.92rem !important;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                text-align: center !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-baseweb="tab-list"] button[aria-selected="true"] {
                background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%) !important;
                color: #FFFFFF !important;
                box-shadow: 0 4px 12px rgba(168, 85, 247, 0.35) !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-baseweb="tab-list"] button:hover {
                color: #F8FAFC !important;
            }
            
            /* Custom Inputs Focus Glow & Spacious Layout styling */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stTextInput"] input {
                background-color: rgba(2, 6, 23, 0.5) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #F8FAFC !important;
                border-radius: 12px !important;
                padding: 12px 16px !important;
                font-size: 0.95rem !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="stTextInput"] input:focus {
                border-color: #a855f7 !important;
                box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2), 0 0 20px rgba(99, 102, 241, 0.15) !important;
                background-color: rgba(15, 23, 42, 0.75) !important;
            }
            
            /* Hide 'Press Enter to apply' tooltip instruction to avoid eye icon overlap */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div[data-testid="InputInstructions"] {
                display: none !important;
                visibility: hidden !important;
                height: 0px !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) label[data-testid="stWidgetLabel"] p {
                font-size: 0.9rem !important;
                font-weight: 600 !important;
                color: #E2E8F0 !important;
                margin-bottom: 8px !important;
                letter-spacing: 0.3px !important;
            }
            
            /* Full width premium Action Button with mixed colors gradient */
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div.stButton > button {
                background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%) !important;
                color: white !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                padding: 14px 24px !important;
                font-weight: 700 !important;
                font-size: 0.98rem !important;
                letter-spacing: 0.5px !important;
                width: 100%;
                box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3) !important;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div.stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 24px rgba(236, 72, 153, 0.4), 0 0 20px rgba(99, 102, 241, 0.2) !important;
                background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f43f5e 100%) !important;
                border-color: rgba(255, 255, 255, 0.25) !important;
            }
            
            [data-testid="stAppViewContainer"]:has(#login-page-marker) div.stButton > button:active {
                transform: translateY(0px) !important;
                box-shadow: 0 4px 10px rgba(99, 102, 241, 0.25) !important;
            }
            
            /* Ensure layout is scrollable if needed */
            [data-testid="stAppViewContainer"] {
                overflow-y: auto !important;
            }

            /* Premium Header Logo & Brand styles with mixed dark gradient background */
            .login-logo-container {
                margin-top: 10px;
                margin-bottom: 25px;
                text-align: center;
                position: relative;
            }
            .login-logo-radial {
                position: absolute;
                top: -15px;
                left: 50%;
                transform: translateX(-50%);
                width: 140px;
                height: 140px;
                background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%);
                filter: blur(20px);
                pointer-events: none;
                z-index: 0;
            }
            .login-logo-badge {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 74px !important;
                height: 74px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #0b0f19 0%, #1d152b 100%) !important;
                border: 2px solid rgba(168, 85, 247, 0.6) !important;
                box-shadow: 0 0 25px rgba(168, 85, 247, 0.35) !important;
                margin-bottom: 18px !important;
                position: relative !important;
                z-index: 1 !important;
                animation: badge-pulse 3s ease-in-out infinite alternate !important;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
                cursor: pointer;
            }
            .login-logo-badge:hover {
                transform: scale(1.12) rotate(15deg) !important;
                border-color: #ec4899 !important;
                box-shadow: 0 0 35px rgba(236, 72, 153, 0.55), 0 0 15px rgba(99, 102, 241, 0.25) !important;
            }
            .login-logo-emoji {
                font-size: 2.4rem !important;
                filter: drop-shadow(0 4px 12px rgba(168, 85, 247, 0.45)) !important;
                display: inline-block !important;
                transition: transform 0.4s ease !important;
            }
            .login-logo-badge:hover .login-logo-emoji {
                transform: scale(1.05) !important;
            }
            @keyframes badge-pulse {
                0% {
                    box-shadow: 0 0 15px rgba(99, 102, 241, 0.25);
                    border-color: rgba(99, 102, 241, 0.45);
                }
                100% {
                    box-shadow: 0 0 35px rgba(168, 85, 247, 0.55), 0 0 15px rgba(99, 102, 241, 0.25);
                    border-color: rgba(236, 72, 153, 0.7);
                }
            }
            .login-title {
                font-size: 2.0rem !important;
                font-weight: 800 !important;
                background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #ec4899 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                margin: 0 0 8px 0 !important;
                letter-spacing: -0.03em !important;
                position: relative !important;
                z-index: 1 !important;
                transition: all 0.3s ease !important;
            }
            .login-title:hover {
                letter-spacing: -0.01em !important;
                filter: drop-shadow(0 0 20px rgba(236, 72, 153, 0.35)) !important;
            }
            .login-desc {
                color: #94A3B8 !important;
                font-size: 0.88rem !important;
                font-weight: 500 !important;
                line-height: 1.5 !important;
                max-width: 400px !important;
                margin: 0 auto !important;
                position: relative !important;
                z-index: 1 !important;
            }
        </style>
    """), unsafe_allow_html=True)



    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown('<div class="login-logo-container"><div class="login-logo-radial"></div><div class="login-logo-badge"><span class="login-logo-emoji">✈️</span></div><h1 class="login-title">AI Travel Concierge</h1><p class="login-desc">Your premium, intelligent partner for day-by-day itineraries, budgeting, and voice exploration.</p></div>', unsafe_allow_html=True)
        
        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with auth_tab1:
            st.markdown("<div style='height: 1px; background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0) 100%); margin: 20px 0;'></div>", unsafe_allow_html=True)
            login_username = st.text_input("Username", placeholder="Enter your username", key="login_username_input").strip()
            login_password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password_input").strip()
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Sign In to Concierge", key="login_submit_btn", use_container_width=True):
                if not login_username or not login_password:
                    st.error("Please enter both username and password.")
                elif verify_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.needs_scroll_to_top = True
                    # Initialize default user chat history
                    st.session_state.messages = [
                        {
                            "role": "assistant",
                            "content": f"👋 Welcome back, {login_username}! I am your AI Travel Concierge. How can I help you today?"
                        }
                    ]
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    
        with auth_tab2:
            st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.08); margin: 15px 0;'>", unsafe_allow_html=True)
            reg_username = st.text_input("Choose Username", placeholder="e.g. wanderer42", key="reg_username_input").strip()
            reg_password = st.text_input("Choose Password", type="password", placeholder="Minimum 6 characters", key="reg_password_input").strip()
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="reg_confirm_input").strip()
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Register & Create Account", key="reg_submit_btn", use_container_width=True):
                if not reg_username or not reg_password:
                    st.error("Please fill in all fields.")
                elif len(reg_username) < 3:
                    st.error("Username must be at least 3 characters long.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                elif user_exists(reg_username):
                    st.error("Username is already taken. Please choose another one.")
                else:
                    if create_user(reg_username, reg_password):
                        st.success("Account created successfully! You can now log in using the 'Sign In' tab.")
                    else:
                        st.error("Registration failed. Please try again.")
                        

    st.stop()
 
# Scroll to top of the page if flag is set (e.g. right after login)
if st.session_state.get("needs_scroll_to_top", False):
    components.html(
        """
        <script>
            setTimeout(() => {
                try {
                    const scrollContainers = [
                        window.parent.document.querySelector('[data-testid="stAppViewContainer"]'),
                        window.parent.document.querySelector('.main'),
                        window.parent.window
                    ];
                    scrollContainers.forEach(el => {
                        if (el) {
                            if (el.scrollTo) {
                                el.scrollTo(0, 0);
                            } else {
                                el.scrollTop = 0;
                            }
                        }
                    });
                } catch (e) {
                    console.error("Scroll to top failed:", e);
                }
            }, 200);
        </script>
        """,
        height=0,
        width=0
    )
    st.session_state.needs_scroll_to_top = False

# Premium Main Header (rendered only when logged in)
st.markdown(f"""
    <div class="main-header">
        <div class="header-logo">
            <span style="font-size: 1.8rem; animation: float 4s ease-in-out infinite; display: inline-block;">✈️</span>
            <span class="header-title">AI Travel Concierge</span>
        </div>
        <div class="header-user-status">
            <div class="pulse-indicator"></div>
            <span style="color: #E2E8F0;">Active Session: <strong style="color: #818CF8;">{st.session_state.username}</strong></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Declare voice assistant custom component
voice_assistant_component = components.declare_component(
    "voice_assistant",
    path=os.path.join(os.path.dirname(__file__), "voice_component")
)

# Sidebar Branding & Voice Assistant
with st.sidebar:
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1.5rem; margin-top: 0rem;">
            <span style="font-size: 3.5rem;">🌍</span>
            <h3 class="sidebar-title">AI Concierge</h3>
            <p class="sidebar-user-info">Logged in as: <strong style="color: #6366F1;">{st.session_state.username}</strong></p>
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)
    
    # Get last assistant response to play text-to-speech if configured
    last_assistant_msg = ""
    if st.session_state.get("message_to_speak"):
        last_assistant_msg = st.session_state.message_to_speak
        st.session_state.message_to_speak = None  # Clear after reading so it only plays once
        
    read_aloud_enabled = st.session_state.get("read_aloud_toggle", True)
    
    # Render voice assistant card in sidebar
    st.markdown('<div class="highlight-card" style="padding: 15px; margin-bottom: 15px;">', unsafe_allow_html=True)
    st.markdown("<p style='margin:0 0 10px 0; font-size:0.85rem; color:#94A3B8; font-weight: 600; text-align: center;'>🎙️ Voice Assistant Panel</p>", unsafe_allow_html=True)
    voice_data = voice_assistant_component(
        key="voice_rec_widget",
        last_assistant_msg=last_assistant_msg,
        read_aloud=read_aloud_enabled,
        height=60
    )
    st.checkbox("🔊 Read assistant replies aloud", value=True, key="read_aloud_toggle")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if a new voice translation is received
    if voice_data and isinstance(voice_data, dict) and "text" in voice_data:
        v_text = voice_data["text"]
        v_ts = voice_data["timestamp"]
        if st.session_state.get("last_voice_timestamp", 0) != v_ts:
            st.session_state.last_voice_timestamp = v_ts
            if v_text.strip():
                st.session_state.messages.append({"role": "user", "content": v_text})
                st.session_state.voice_redirect = True
                st.rerun()

    st.info("💡 **Tip:** Ask our Chat Assistant about local dining or weather forecasts in any region.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Log Out", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        # Reset chat session state
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I am your AI Travel Concierge. Ask me anything about destinations, weather, or travel tips."
            }
        ]
        if "navigation_pills" in st.session_state:
            st.session_state.navigation_pills = "💬 Chat Assistant"
        st.rerun()

@st.dialog("🗺️ Hotel Map Location", width="large")
def show_hotel_map_dialog(name, lat, lon, hotels_list):
    map_style_val = st.session_state.get("map_style", "Google Roadmap")
    hotel_map = create_hotel_map(
        lat,
        lon,
        name,
        hotels_list,
        tiles=map_style_val
    )
    st_folium(
        hotel_map,
        center=(lat, lon),
        zoom=15,
        height=550,
        use_container_width=True,
        key=f"dialog_hotel_map_{str(lat).replace('.', '_')}_{str(lon).replace('.', '_')}"
    )
# Setup horizontal tab navigation (10 tabs total) using st.pills
active_page = st.pills(
    label="Navigation",
    options=[
        "💬 Chat Assistant",
        "📅 AI Trip Planner",
        "🛫 Flights",
        "🎭 Mood & Vibe",
        "🏨 Hotels & Stays",
        "🔍 Nearby Explorer",
        "💰 Budget Calculator",
        "🗺️ Interactive Maps",
        "🧳 Packing Assistant",
        "📜 Search History"
    ],
    default="💬 Chat Assistant",
    key="navigation_pills",
    label_visibility="collapsed"
)


# ------------------------------------------------
# 1. Chat Assistant
# ------------------------------------------------
if active_page == "💬 Chat Assistant":
    st.markdown("### 💬 Conversational Chatbot")
    
    # Initialize message list in state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I am your AI Travel Concierge. Ask me anything about destinations, weather, or travel tips."
            }
        ]
        

        
    # Render all past messages in history (wrapped with helper tags for left/right styling)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg-container"></div>{msg["content"]}', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-msg-container"></div>{msg["content"]}', unsafe_allow_html=True)
            
    # Check if a suggestion chip was clicked in the last run
    if "chat_query" in st.session_state and st.session_state.chat_query:
        query = st.session_state.chat_query
        st.session_state.chat_query = None  # Reset suggestion state
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()
        
    # Quick suggestion chips
    st.markdown("<div style='margin-top: 20px; margin-bottom: 10px; font-size: 0.9rem; color: #94A3B8; font-weight: 500;'>Quick Suggestions:</div>", unsafe_allow_html=True)
    st.markdown('<div class="suggestion-pills-marker"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌤️ Weather in Paris", key="btn_weather_paris", use_container_width=True):
            st.session_state.chat_query = "What is the weather in Paris?"
            st.rerun()
    with col2:
        if st.button("💡 Tokyo travel tips", key="btn_tips_tokyo", use_container_width=True):
            st.session_state.chat_query = "Give me travel tips for Tokyo?"
            st.rerun()
    with col3:
        if st.button("🏖️ Suggest beach vacation", key="btn_suggest_beach", use_container_width=True):
            st.session_state.chat_query = "Suggest a beach vacation destination"
            st.rerun()
            
    # Check if last message is from user. If so, generate assistant response.
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_query = st.session_state.messages[-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("Consulting travel experts..."):
                response = ask_agent(user_query)
                st.markdown(f'<div class="assistant-msg-container"></div>{response}', unsafe_allow_html=True)
                # Save query scoped to user session in local SQLite database
                try:
                    save_search(st.session_state.username, user_query, response)
                except Exception as e:
                    pass
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.message_to_speak = response
        st.rerun()
        
    # Chat Input Box
    if prompt := st.chat_input("Ask anything about weather, travel tips, local foods..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()


# ------------------------------------------------
# 2. AI Trip Planner
# ------------------------------------------------
elif active_page == "📅 AI Trip Planner":
    st.markdown("### 📅 AI Trip Planner")
    
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Configure Your Dream Trip</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Fill in the details below, and our AI will curate a personalized day-by-day travel itinerary just for you.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("📍 Destination", placeholder="e.g. Kyoto, Japan", key="planner_dest")
    with col2:
        days = st.slider("📅 Number of Days", min_value=1, max_value=30, value=5, key="planner_days")

    col3, col4 = st.columns(2)
    with col3:
        travel_style = st.selectbox(
            "🎭 Travel Style",
            ["Balanced", "Adventure", "Luxury", "Budget Friendly", "Family Focused", "Relaxed & Leisure"],
            key="planner_style"
        )
    with col4:
        special_interests = st.text_input("✨ Special Interests (Optional)", placeholder="e.g. temples, local food, photo spots", key="planner_interests")
        
    # Generate Itinerary Button
    if st.button("🚀 Generate Itinerary", key="planner_submit"):
        if not destination:
            st.error("Please specify a destination!")
        else:
            with st.spinner(f"Curating your personalized {days}-day itinerary to {destination}..."):
                style_str = f"Style: {travel_style}"
                if special_interests:
                    style_str += f", Interests: {special_interests}"
                
                dest_formatted = f"{destination} ({style_str})"
                try:
                    itinerary = generate_itinerary(dest_formatted, days)
                    
                    # Save to SQLite database
                    try:
                        save_search(st.session_state.username, f"Generated {days}-day itinerary for {destination} ({style_str})", itinerary)
                    except Exception as e:
                        pass
                    
                    st.session_state.itinerary_result = itinerary
                    st.session_state.itinerary_dest = destination
                    st.session_state.itinerary_days = days
                except Exception as e:
                    st.error(f"Failed to generate itinerary: {e}")

    # Display itinerary if it exists in state
    if "itinerary_result" in st.session_state:
        st.markdown(f"### 📍 Personalized Itinerary for {st.session_state.itinerary_dest}")
        
        # PDF export button
        try:
            pdf_bytes = generate_itinerary_pdf(
                st.session_state.itinerary_dest,
                st.session_state.itinerary_days,
                st.session_state.get("planner_style", "Balanced"),
                st.session_state.get("planner_interests", ""),
                st.session_state.itinerary_result
            )
            filename = f"Itinerary_{st.session_state.itinerary_dest.replace(' ', '_').replace(',', '')}.pdf"
            st.download_button(
                label="📥 Download PDF Itinerary",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                key="download_pdf_itinerary"
            )
        except Exception as pdf_err:
            st.error(f"Error generating PDF export: {pdf_err}")
            
        # Parse and display day-by-day in expanders
        itinerary_text = st.session_state.itinerary_result
        days_data = re.split(r"(?i)##?\s*Day\s*(\d+)", itinerary_text)
        
        if len(days_data) > 1:
            intro = days_data[0].strip()
            if intro:
                st.markdown(f"<div class='highlight-card'>{intro}</div>", unsafe_allow_html=True)
                
            for i in range(1, len(days_data), 2):
                day_num = days_data[i]
                day_content = days_data[i+1].strip()
                # Clean up leading formatting symbols
                day_content_cleaned = re.sub(r"^[:\s\-]*", "", day_content)
                
                with st.expander(f"📅 Day {day_num}", expanded=(i==1)):
                    st.markdown(day_content_cleaned)
        else:
            st.markdown(f"<div class='highlight-card'>{itinerary_text}</div>", unsafe_allow_html=True)

# ------------------------------------------------
# 2.5 Flights Tab
# ------------------------------------------------
elif active_page == "🛫 Flights":
    st.markdown("### 🛫 Flight Recommendations")
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Find Recommended Flights</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Enter details below to search for realistic airline options, prices, schedules, and transit points.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        flight_origin = st.text_input("🛫 Origin City / Airport", placeholder="e.g. New Delhi (DEL)", key="flight_origin_input")
        flight_dest = st.text_input("🛬 Destination City / Airport", placeholder="e.g. London (LHR)", key="flight_dest_input")
    with col2:
        import datetime
        flight_date = st.date_input("📅 Departure Date", value=datetime.date.today() + datetime.timedelta(days=14), key="flight_date_input")
        flight_class = st.selectbox(
            "💺 Travel Class",
            ["Economy", "Premium Economy", "Business Class", "First Class"],
            key="flight_class_select"
        )
        
    if st.button("✈️ Search Flights", key="flight_search_btn", use_container_width=True):
        if not flight_origin.strip() or not flight_dest.strip():
            st.error("Please fill in both Origin and Destination airports.")
        else:
            with st.spinner(f"Searching for {flight_class.lower()} flights from {flight_origin} to {flight_dest}..."):
                # Call agent recommendations
                flights = get_flight_recommendations(flight_origin.strip(), flight_dest.strip(), str(flight_date), flight_class)
                st.session_state.flight_recommendations = flights
                st.session_state.flight_search_origin = flight_origin.strip()
                st.session_state.flight_search_dest = flight_dest.strip()
                st.session_state.flight_search_date = str(flight_date)
                st.session_state.flight_search_class = flight_class
                
    if "flight_recommendations" in st.session_state:
        st.markdown(f"### ✈️ Curated Flights: {st.session_state.flight_search_origin} ➔ {st.session_state.flight_search_dest} ({st.session_state.flight_search_class})")
        st.markdown(f"<p style='color: #94A3B8; font-size: 0.95rem; margin-top: -10px; margin-bottom: 20px;'>Departing on: <strong>{st.session_state.flight_search_date}</strong></p>", unsafe_allow_html=True)
        
        flights_list = st.session_state.flight_recommendations
        for idx, fl in enumerate(flights_list):
            airline = fl.get("airline", "Global Airlines")
            fnum = fl.get("flight_number", "GL-123")
            d_time = fl.get("departure_time", "08:00 AM")
            a_time = fl.get("arrival_time", "12:00 PM")
            duration = fl.get("duration", "4h 00m")
            layovers = fl.get("layovers", "Non-stop")
            price = fl.get("price", "₹15,000")
            amenities = fl.get("highlights", [])
            
            tags_html = "".join([f'<span class="hotel-tag">{tag}</span>' for tag in amenities])
            
            st.markdown(f"""
                <div class="flight-card">
                    <div class="flight-header">
                        <div class="flight-airline">
                            ✈️ {airline}
                            <span class="flight-number">{fnum}</span>
                        </div>
                        <div class="flight-price">{price}</div>
                    </div>
                    <div class="flight-route-container">
                        <div class="flight-station">
                            <span class="flight-time">{d_time}</span>
                            <span class="flight-city">{st.session_state.flight_search_origin}</span>
                        </div>
                        <div class="flight-path-viz">
                            <div class="flight-line">
                                <span class="flight-icon-path">✈️</span>
                            </div>
                            <span class="flight-duration">{duration}</span>
                            <span class="flight-layovers">{layovers}</span>
                        </div>
                        <div class="flight-station" style="text-align: right;">
                            <span class="flight-time">{a_time}</span>
                            <span class="flight-city">{st.session_state.flight_search_dest}</span>
                        </div>
                    </div>
                    <div class="hotel-tags" style="margin: 0;">
                        {tags_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 15px 0;'>", unsafe_allow_html=True)

# ------------------------------------------------
# 2.8 Mood & Vibe Suggestions Tab
# ------------------------------------------------
elif active_page == "🎭 Mood & Vibe":
    st.markdown("### 🎭 Mood-Based Destination Suggestions")
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Discover Places by Your Emotional Vibe</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Feeling burnt out? Need a healing trip or craving chaotic fun? Tell us how you feel, and the AI will suggest matching spots around the globe based on energy and emotional match, not just budgets.</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize query input in state if not present
    if "mood_query_input_val" not in st.session_state:
        st.session_state.mood_query_input_val = ""

    # Quick selection pills
    st.markdown("<div style='margin-top: 15px; margin-bottom: 8px; font-size: 0.9rem; color: #94A3B8; font-weight: 500;'>How do you feel today?</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🔥 I'm burnt out", key="mood_pill_burn", use_container_width=True):
            st.session_state.mood_query_input_val = "I'm burnt out"
            st.session_state.run_mood_search = True
            st.rerun()
    with col2:
        if st.button("🌫️ Disappear for 3 days", key="mood_pill_disappear", use_container_width=True):
            st.session_state.mood_query_input_val = "I want to disappear for 3 days"
            st.session_state.run_mood_search = True
            st.rerun()
    with col3:
        if st.button("🌿 Healing trip", key="mood_pill_healing", use_container_width=True):
            st.session_state.mood_query_input_val = "Need a healing trip"
            st.session_state.run_mood_search = True
            st.rerun()
    with col4:
        if st.button("🎬 Cinematic sights", key="mood_pill_cinematic", use_container_width=True):
            st.session_state.mood_query_input_val = "I want somewhere cinematic"
            st.session_state.run_mood_search = True
            st.rerun()
    with col5:
        if st.button("⚡ Chaotic fun", key="mood_pill_chaotic", use_container_width=True):
            st.session_state.mood_query_input_val = "chaotic fun"
            st.session_state.run_mood_search = True
            st.rerun()

    # User input
    mood_input = st.text_input(
        "🔮 Describe your vibe / emotional state:",
        value=st.session_state.mood_query_input_val,
        placeholder="e.g. I am tired of work, want to relax near oceans, or I need an exciting adventure...",
        key="mood_text_input"
    )
    
    # Sync input value back to state
    st.session_state.mood_query_input_val = mood_input

    search_clicked = st.button("🎭 Find My Destination", key="mood_search_btn", use_container_width=True)
    
    if search_clicked or st.session_state.get("run_mood_search", False):
        st.session_state.run_mood_search = False  # Reset flag
        query_to_run = st.session_state.mood_query_input_val.strip()
        if not query_to_run:
            st.error("Please enter how you're feeling or select a quick vibe above.")
        else:
            with st.spinner(f"Matching locations for: '{query_to_run}'..."):
                results = get_mood_suggestions(query_to_run)
                st.session_state.mood_suggestions = results
                st.session_state.mood_query_ran = query_to_run
                
                # Save mood search to search history db
                try:
                    save_search(st.session_state.username, f"Mood search: {query_to_run}", f"Suggested: {', '.join([r['name'] for r in results])}")
                except Exception:
                    pass

    if "mood_suggestions" in st.session_state:
        st.markdown(f"### 🔮 Suggestions for: *\"{st.session_state.mood_query_ran}\"*")
        
        # Split layout: 5 columns for cards, 5 for maps
        card_col, map_col = st.columns([5, 5])
        
        with card_col:
            for idx, dest in enumerate(st.session_state.mood_suggestions):
                name = dest.get("name", "Unknown Destination")
                vibe = dest.get("vibe_class", "special vibe")
                duration = dest.get("duration", "3-5 days")
                season = dest.get("best_season", "All year")
                desc = dest.get("description", "A beautiful matching destination for your current state.")
                
                st.markdown(f"""
                    <div class="mood-card">
                        <div class="mood-title">
                            <span>📍 {name}</span>
                            <span class="mood-vibe-tag">{vibe}</span>
                        </div>
                        <div class="mood-meta">
                            <div class="mood-meta-item">⏱️ <b>Duration:</b> {duration}</div>
                            <div class="mood-meta-item">📅 <b>Best Season:</b> {season}</div>
                        </div>
                        <div class="mood-description">
                            {desc}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
        with map_col:
            with st.spinner("Loading interactive vibe map..."):
                mood_map = create_mood_map(st.session_state.mood_suggestions)
                st_folium(
                    mood_map,
                    center=(20, 0),
                    zoom=2,
                    height=500,
                    use_container_width=True,
                    key="folium_mood_map"
                )

# ------------------------------------------------
# 3. Budget Calculator
# ------------------------------------------------
elif active_page == "💰 Budget Calculator":
    st.markdown("### 💰 Budget Calculator")
    
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Estimate Your Expenses</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Input estimated daily costs to calculate a complete trip budget and view allocation percentage breakdown.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        calc_days = st.number_input("📅 Days", min_value=1, max_value=30, value=5, key="budget_days")
        calc_hotel = st.number_input("🏨 Hotel Per Day (₹)", min_value=0, value=3000, step=500, key="budget_hotel")
    with col2:
        calc_food = st.number_input("🍔 Food Per Day (₹)", min_value=0, value=1500, step=250, key="budget_food")
        calc_transport = st.number_input("🚗 Transport Total (₹)", min_value=0, value=5000, step=500, key="budget_transport")

    if st.button("📊 Calculate Budget Breakdown", key="budget_submit"):
        total = calculate_budget(calc_days, calc_hotel, calc_food, calc_transport)
        
        total_hotel = calc_days * calc_hotel
        total_food = calc_days * calc_food
        total_transport = calc_transport
        
        if total > 0:
            pct_hotel = (total_hotel / total) * 100
            pct_food = (total_food / total) * 100
            pct_transport = (total_transport / total) * 100
        else:
            pct_hotel = pct_food = pct_transport = 0
            
        st.session_state.budget_total = total
        st.session_state.budget_total_hotel = total_hotel
        st.session_state.budget_total_food = total_food
        st.session_state.budget_total_transport = total_transport
        st.session_state.budget_pct_hotel = pct_hotel
        st.session_state.budget_pct_food = pct_food
        st.session_state.budget_pct_transport = pct_transport

    # Show calculated budget if total is present in state
    if "budget_total" in st.session_state:
        total = st.session_state.budget_total
        total_hotel = st.session_state.budget_total_hotel
        total_food = st.session_state.budget_total_food
        total_transport = st.session_state.budget_total_transport
        pct_hotel = st.session_state.budget_pct_hotel
        pct_food = st.session_state.budget_pct_food
        pct_transport = st.session_state.budget_pct_transport
        
        # Display Metrics in columns
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Estimated Total", f"₹{total:,}")
        m_col2.metric("Hotel Total", f"₹{total_hotel:,}")
        m_col3.metric("Food Total", f"₹{total_food:,}")
        m_col4.metric("Transport Total", f"₹{total_transport:,}")
        
        # Show visual allocation progress bar
        st.markdown("### 📊 Budget Allocation")
        st.markdown(f"""
            <div class="card-container">
                <div style="font-weight: 600; margin-bottom: 15px; font-size: 1.1rem; color: #F8FAFC;">Expense Split</div>
                <div class="budget-bar-container">
                    <div class="budget-bar-hotel" style="width: {pct_hotel}%;" title="Hotel: {pct_hotel:.1f}%"></div>
                    <div class="budget-bar-food" style="width: {pct_food}%;" title="Food: {pct_food:.1f}%"></div>
                    <div class="budget-bar-transport" style="width: {pct_transport}%;" title="Transport: {pct_transport:.1f}%"></div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 24px; margin-top: 15px; font-size: 0.9rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 12px; height: 12px; background-color: #6366F1; border-radius: 3px;"></div>
                        <span style="color: #F8FAFC; font-weight: 600;">🏨 Hotel:</span>
                        <span style="color: #94A3B8;">{pct_hotel:.1f}% (₹{total_hotel:,})</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 12px; height: 12px; background-color: #10B981; border-radius: 3px;"></div>
                        <span style="color: #F8FAFC; font-weight: 600;">🍔 Food:</span>
                        <span style="color: #94A3B8;">{pct_food:.1f}% (₹{total_food:,})</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 12px; height: 12px; background-color: #F59E0B; border-radius: 3px;"></div>
                        <span style="color: #F8FAFC; font-weight: 600;">🚗 Transport:</span>
                        <span style="color: #94A3B8;">{pct_transport:.1f}% (₹{total_transport:,})</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------
# 4. Hotels & Stays
# ------------------------------------------------


elif active_page == "🏨 Hotels & Stays":
    st.markdown("### 🏨 Hotel Recommendations")
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Find Your Perfect Stay</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Enter a destination and select your desired budget level to get curated recommendations powered by our AI travel model.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        hotel_dest = st.text_input("📍 Destination City / Region", placeholder="e.g. Tokyo, Paris, Rome...", key="hotel_dest_input")
    with col2:
        hotel_budget = st.selectbox(
            "💰 Budget Class",
            ["Luxury & Resorts", "Premium / Boutique", "Budget-friendly", "Heritage / Historic"],
            key="hotel_budget_select"
        )
        
    if st.button("🔍 Search Hotels", key="hotel_search_btn", use_container_width=True):
        if not hotel_dest.strip():
            st.error("Please enter a destination to search for stays.")
        else:
            with st.spinner(f"Finding perfect {hotel_budget.lower()} stays in {hotel_dest}..."):
                recommendations = get_hotel_recommendations(hotel_dest.strip(), hotel_budget)
                
                from src.tools.travel_tools import geocode_place
                valid_recs = []
                for hotel in recommendations:
                    hname = hotel.get("name", "")
                    lat_h, lon_h, _ = geocode_place(f"{hname}, {hotel_dest.strip()}")
                    if lat_h is not None and lon_h is not None:
                        hotel["lat"] = lat_h
                        hotel["lon"] = lon_h
                    valid_recs.append(hotel)
                
                st.session_state.hotel_recommendations = valid_recs
                st.session_state.hotel_search_dest = hotel_dest.strip()
                st.session_state.hotel_search_budget = hotel_budget
                
                # Geocode city center
                lat_c, lon_c, _ = geocode_place(hotel_dest.strip())
                if lat_c is not None and lon_c is not None:
                    st.session_state.hotel_city_lat = lat_c
                    st.session_state.hotel_city_lon = lon_c
                else:
                    first_coords = next(((h["lat"], h["lon"]) for h in valid_recs if "lat" in h), (13.0827, 80.2707))
                    st.session_state.hotel_city_lat = first_coords[0]
                    st.session_state.hotel_city_lon = first_coords[1]
                
                st.session_state.selected_hotel_lat = st.session_state.hotel_city_lat
                st.session_state.selected_hotel_lon = st.session_state.hotel_city_lon
                st.session_state.selected_hotel_name = hotel_dest.strip()
                
    if "hotel_recommendations" in st.session_state:
        st.markdown(f"### 🌟 Curated Stays in {st.session_state.hotel_search_dest} ({st.session_state.hotel_search_budget})")
        
        recs = st.session_state.hotel_recommendations
        
        # Display in a grid of 3 columns
        cols = st.columns(3)
        for idx, hotel in enumerate(recs):
            col = cols[idx % 3]
            with col:
                name = hotel.get("name", "Exclusive Hotel")
                price = hotel.get("price_range", "N/A")
                rating = hotel.get("rating", 4.5)
                htype = hotel.get("type", "Boutique")
                highlights = hotel.get("highlights", [])
                desc = hotel.get("description", "")
                
                tags_html = "".join([f'<span class="hotel-tag">{tag}</span>' for tag in highlights])
                
                st.markdown(f"""
                    <div class="hotel-card" style="margin-bottom: 8px; min-height: 260px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div class="hotel-header">
                                <h4 class="hotel-title" style="margin: 0; color: #F8FAFC;">{name}</h4>
                                <span class="hotel-rating" style="color: #F59E0B; font-weight: bold;">★ {rating}</span>
                            </div>
                            <div class="hotel-price" style="font-size: 0.9rem; color: #10B981; margin: 4px 0;">💰 {price} | {htype}</div>
                            <p class="hotel-desc" style="font-size: 0.85rem; color: #94A3B8; margin: 4px 0 8px 0; line-height: 1.4;">{desc}</p>
                            <div class="hotel-tags" style="margin-top: auto;">
                                {tags_html}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                lat_h = hotel.get("lat")
                lon_h = hotel.get("lon")
                
                if lat_h is not None and lon_h is not None:
                    if st.button(f"🗺️ View on Map", key=f"hotel_map_{idx}", use_container_width=True):
                        show_hotel_map_dialog(name, lat_h, lon_h, recs)
                else:
                    st.caption("Coordinates not found.")
                st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 10px 0;'>", unsafe_allow_html=True)

# ------------------------------------------------
# 5. Nearby Explorer
# ------------------------------------------------
elif active_page == "🔍 Nearby Explorer":
    st.markdown("### 🔍 Nearby Places Explorer")
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Explore Points of Interest</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Select a location and a category to see a detailed list and an interactive multi-marker map of nearby venues and hotspots.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        poi_loc = st.text_input("📍 Explorer Location", placeholder="e.g. Rome, Tokyo Shinjuku, Paris Montmartre...", key="poi_loc_input")
    with col_p2:
        poi_cat = st.selectbox(
            "🎭 Category of Interest",
            [
                "🍽️ Restaurants & Dining",
                "🏛️ Tourist Attractions",
                "☕ Cafes & Bars",
                "🛍️ Shopping & Malls",
                "🌳 Parks & Nature"
            ],
            key="poi_cat_select"
        )
        
    if st.button("🚀 Search Nearby", key="poi_search_btn", use_container_width=True):
        if not poi_loc.strip():
            st.error("Please specify a location to explore!")
        else:
            with st.spinner(f"Exploring {poi_cat.lower()} around '{poi_loc}'..."):
                from src.tools.travel_tools import geocode_place
                lat_c, lon_c, label_c = geocode_place(poi_loc.strip())
                if lat_c is not None and lon_c is not None:
                    places = get_nearby_places(poi_loc.strip(), poi_cat)
                    st.session_state.poi_places = places
                    st.session_state.poi_lat = lat_c
                    st.session_state.poi_lon = lon_c
                    st.session_state.poi_label = label_c
                    st.session_state.poi_loc_name = poi_loc.strip()
                    st.session_state.poi_category = poi_cat
                else:
                    st.error(f"Could not resolve the location '{poi_loc}'. Please try a different name.")
                    
    if "poi_places" in st.session_state:
        st.markdown(f"### 📍 {st.session_state.poi_category} near {st.session_state.poi_label}")
        
        places = st.session_state.poi_places
        
        if not places:
            st.warning("No nearby places found in this category. Try a broader location or another category.")
        else:
            split_col1, split_col2 = st.columns([2, 3])
            
            with split_col1:
                st.markdown("<div style='max-height: 500px; overflow-y: auto; padding-right: 10px;'>", unsafe_allow_html=True)
                for item in places:
                    name = item.get("name", "POI")
                    addr = item.get("address", "No address info")
                    ptype = item.get("type", "POI")
                    
                    st.markdown(f"""
                        <div class="poi-card">
                            <span class="poi-type">{ptype}</span>
                            <h5 class="poi-title">{name}</h5>
                            <p class="poi-addr">{addr}</p>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with split_col2:
                with st.spinner("Rendering explorer map..."):
                    map_style_val = st.session_state.get("map_style", "Google Roadmap")
                    multi_map = create_multi_marker_map(
                        st.session_state.poi_lat,
                        st.session_state.poi_lon,
                        st.session_state.poi_label,
                        places,
                        tiles=map_style_val
                    )
                    st_folium(
                        multi_map,
                        center=(st.session_state.poi_lat, st.session_state.poi_lon),
                        zoom=13,
                        height=500,
                        use_container_width=True,
                        key="folium_explorer"
                    )

# ------------------------------------------------
# 6. Interactive Maps
# ------------------------------------------------
elif active_page == "🗺️ Interactive Maps":
    st.markdown("### 🗺️ Interactive Maps")
    
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Explore Destinations</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Select a popular travel destination to auto-populate coordinates or input custom coordinates. Customize map themes to match the sleek dark interface.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Preset coordinate options
    presets = {
        "Select a City": None,
        "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503},
        "Paris, France": {"lat": 48.8566, "lon": 2.3522},
        "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
        "Chennai, India": {"lat": 13.0827, "lon": 80.2707},
        "New York, USA": {"lat": 40.7128, "lon": -74.0060},
        "London, UK": {"lat": 51.5074, "lon": -0.1278},
        "Rome, Italy": {"lat": 41.9028, "lon": 12.4964}
    }
    
    # Callback functions to synchronize inputs
    def sync_preset_to_custom():
        if st.session_state.map_preset != "Select a City":
            st.session_state.map_custom_place = ""

    def sync_custom_to_preset():
        if st.session_state.map_custom_place.strip():
            st.session_state.map_preset = "Select a City"

    col1, col2 = st.columns(2)
    with col1:
        selected_preset = st.selectbox(
            "🌐 Quick Select Popular City",
            list(presets.keys()),
            key="map_preset",
            on_change=sync_preset_to_custom
        )
    with col2:
        map_style = st.selectbox(
            "🎨 Map Style Theme",
            ["Google Roadmap", "Google Satellite", "Google Hybrid", "Google Terrain", "CartoDB Dark_Matter"],
            key="map_style"
        )
        
    custom_place = st.text_input(
        "🔍 Or Search Any Custom Place Name",
        placeholder="e.g. Sydney, Mumbai, Cape Town, Reykjavik...",
        key="map_custom_place",
        on_change=sync_custom_to_preset
    )
        
    if st.button("🗺️ Show Map", key="map_submit", use_container_width=True):
        lat_val = None
        lon_val = None
        label_val = ""
        
        # Check custom search input first
        if custom_place.strip():
            from src.tools.travel_tools import geocode_place
            
            with st.spinner(f"Searching for '{custom_place}'..."):
                lat_val, lon_val, resolved_label = geocode_place(custom_place.strip())
                if lat_val is not None and lon_val is not None:
                    label_val = resolved_label
                    # Save the map query to database search history
                    try:
                        save_search(st.session_state.username, f"Map lookup: {custom_place.strip()}", f"Resolved: {label_val} (Lat {lat_val}, Lon {lon_val})")
                    except Exception:
                        pass
                else:
                    st.error(f"Could not resolve '{custom_place}' to a location. Please try a different place name.")
                    st.session_state.map_show = False
        elif selected_preset != "Select a City":
            coords = presets[selected_preset]
            lat_val = coords["lat"]
            lon_val = coords["lon"]
            label_val = selected_preset.split(",")[0]
        else:
            # Default fallback
            lat_val = 13.0827
            lon_val = 80.2707
            label_val = "Chennai"
            
        if lat_val is not None and lon_val is not None:
            st.session_state.map_show = True
            st.session_state.map_lat_val = lat_val
            st.session_state.map_lon_val = lon_val
            st.session_state.map_label_val = label_val
            st.session_state.map_style_val = map_style
            
    # Render Map if button clicked
    if st.session_state.get("map_show", False):
        lat_val = st.session_state.map_lat_val
        lon_val = st.session_state.map_lon_val
        label_val = st.session_state.map_label_val
        style_val = st.session_state.map_style_val
        
        with st.spinner("Generating interactive map..."):
            travel_map = create_map(
                lat_val,
                lon_val,
                label_val,
                tiles=style_val
            )
            
            st_folium(
                travel_map,
                center=(lat_val, lon_val),
                zoom=12,
                height=500,
                use_container_width=True,
                key="folium_render"
            )

# ------------------------------------------------
# Packing Assistant Tab
# ------------------------------------------------
elif active_page == "🧳 Packing Assistant":
    st.markdown("### 🧳 AI Packing Assistant")
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">Personalized Travel Packing Checklists</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">Generate a custom packing list optimized for your destination, weather, duration, and trip activity class. Add your own items and keep track of your packing status interactively.</p>
        </div>
    """, unsafe_allow_html=True)
    
    pack_col1, pack_col2, pack_col3 = st.columns(3)
    with pack_col1:
        pack_dest = st.text_input("📍 Destination", placeholder="e.g. Switzerland, Goa, Tokyo...", key="pack_dest_input")
        pack_days = st.number_input("📅 Trip Duration (Days)", min_value=1, max_value=60, value=5, step=1, key="pack_days_input")
    with pack_col2:
        pack_type = st.selectbox(
            "🧗 Activity / Trip Type",
            ["Casual/Sightseeing", "Adventure & Hiking", "Beach & Tropical", "Business / Professional", "Romantic Getaway", "Winter Sports"],
            key="pack_type_input"
        )
    with pack_col3:
        pack_season = st.selectbox(
            "☀️ Season / Weather",
            ["Summer / Warm", "Winter / Cold", "Spring / Autumn", "Monsoon / Rainy"],
            key="pack_season_input"
        )
        
    if st.button("🚀 Generate Custom Packing List", key="pack_generate_btn", use_container_width=True):
        if not pack_dest.strip():
            st.error("Please enter a destination to generate the checklist.")
        else:
            with st.spinner(f"AI is preparing your packing checklist for {pack_dest}..."):
                # Fetch packing list
                list_data = get_packing_list(pack_dest.strip(), pack_days, pack_type, pack_season)
                
                # Transform to state with checked states
                state_list = {}
                for category, items in list_data.items():
                    state_list[category] = [{"name": item, "checked": False} for item in items]
                
                st.session_state.current_packing_list = state_list
                st.session_state.pack_search_dest = pack_dest.strip()
                st.session_state.pack_search_days = pack_days
                st.session_state.pack_search_type = pack_type
                st.session_state.pack_search_season = pack_season
                st.rerun()

    if "current_packing_list" in st.session_state:
        st.markdown(f"### 📋 Packing List for **{st.session_state.pack_search_dest}** ({st.session_state.pack_search_days} days | {st.session_state.pack_search_type})")
        
        packing_data = st.session_state.current_packing_list
        
        # Grid of Categories (3 columns)
        p_cols = st.columns(3)
        
        categories = list(packing_data.keys())
        for idx, category in enumerate(categories):
            col_slot = p_cols[idx % 3]
            with col_slot:
                st.markdown(f"""
                    <div class="packing-category-header">
                        <h4 class="packing-category-title">
                            📁 {category}
                        </h4>
                    </div>
                """, unsafe_allow_html=True)
                
                items = packing_data[category]
                
                # Render interactive checkboxes
                for item_idx, item_obj in enumerate(items):
                    item_name = item_obj["name"]
                    is_checked = item_obj["checked"]
                    
                    # Create a unique checkbox key
                    cb_key = f"pack_{category}_{idx}_{item_idx}"
                    
                    checked = st.checkbox(item_name, value=is_checked, key=cb_key)
                    if checked != is_checked:
                        st.session_state.current_packing_list[category][item_idx]["checked"] = checked
                        
                # Add Custom Item Option
                new_item_key = f"new_item_input_{category}_{idx}"
                new_item_btn_key = f"new_item_btn_{category}_{idx}"
                
                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                new_item_val = st.text_input("Add item", placeholder="e.g. Sunhat, Sandals...", key=new_item_key, label_visibility="collapsed")
                if st.button("➕ Add", key=new_item_btn_key, use_container_width=True):
                    if new_item_val.strip():
                        st.session_state.current_packing_list[category].append({"name": new_item_val.strip(), "checked": False})
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
        # Export Option
        st.markdown("---")
        export_col1, export_col2 = st.columns([2, 1])
        with export_col1:
            # Calculate completion percentage
            total_items = 0
            packed_items = 0
            for cat, items in packing_data.items():
                for item in items:
                    total_items += 1
                    if item["checked"]:
                        packed_items += 1
            
            if total_items > 0:
                pct_packed = (packed_items / total_items) * 100
                st.progress(pct_packed / 100)
                st.write(f"🎉 **{packed_items}/{total_items} items packed** ({pct_packed:.0f}%)")
            
        with export_col2:
            # Build plain text export string
            txt_content = f"PACKING LIST FOR {st.session_state.pack_search_dest.upper()}\n"
            txt_content += f"Duration: {st.session_state.pack_search_days} Days | Type: {st.session_state.pack_search_type} | Season: {st.session_state.pack_search_season}\n"
            txt_content += "="*50 + "\n\n"
            for cat, items in packing_data.items():
                txt_content += f"[{cat.upper()}]\n"
                for item in items:
                    status = "[X]" if item["checked"] else "[ ]"
                    txt_content += f" {status} {item['name']}\n"
                txt_content += "\n"
            
            st.download_button(
                label="📥 Download Packing List (.txt)",
                data=txt_content,
                file_name=f"packing_list_{st.session_state.pack_search_dest.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                use_container_width=True
            )



# ------------------------------------------------
# 7. Saved History
# ------------------------------------------------
elif active_page == "📜 Search History":
    st.markdown("### 📜 Saved Trips & History")
    
    st.markdown("""
        <div class="card-container">
            <h4 style="margin:0 0 10px 0; color:#F8FAFC;">History Dashboard</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin:0;">View past searches, travel tip requests, and generated itineraries stored in your local SQLite database.</p>
        </div>
    """, unsafe_allow_html=True)
    
    recent_searches = get_recent_searches(st.session_state.username, 15)
    
    if not recent_searches:
        st.info("No saved history found yet. Start interacting with the Chat Assistant or AI Trip Planner to build history!")
    else:
        for idx, (query, result) in enumerate(recent_searches):
            # Form clean header
            short_query = query[:70] + "..." if len(query) > 70 else query
            with st.expander(f"🔍 {short_query}", expanded=(idx==0)):
                st.markdown(f"**Query/Prompt:**\n\n`{query}`")
                st.markdown("---")
                st.markdown("**AI Response / Plan:**")
                st.markdown(result)