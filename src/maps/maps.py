import folium


def _get_map_args(tiles_style):
    google_styles = {
        "Google Roadmap": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "Google Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "Google Hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "Google Terrain": "https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}",
    }
    
    # Map OpenStreetMap or empty default tiles to Google Roadmap
    if tiles_style == "OpenStreetMap" or not tiles_style:
        tiles_style = "Google Roadmap"
        
    if tiles_style in google_styles:
        return {
            "tiles": google_styles[tiles_style],
            "attr": "Google"
        }
    return {
        "tiles": tiles_style
    }


def create_map(latitude, longitude, place_name, tiles="Google Roadmap"):
    map_args = _get_map_args(tiles)
    travel_map = folium.Map(
        location=[latitude, longitude],
        zoom_start=12,
        **map_args
    )

    folium.Marker(
        [latitude, longitude],
        popup=place_name
    ).add_to(travel_map)

    return travel_map


def create_multi_marker_map(center_lat, center_lon, center_name, markers_list, tiles="Google Roadmap"):
    map_args = _get_map_args(tiles)
    travel_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        **map_args
    )
    
    # Highlight main center location
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>Center: {center_name}</b>",
        tooltip=center_name,
        icon=folium.Icon(color="red", icon="star")
    ).add_to(travel_map)
    
    # Mark all nearby places
    for item in markers_list:
        folium.Marker(
            [item["lat"], item["lon"]],
            popup=f"<b>{item['name']}</b><br>{item['type']}<br>{item['address']}",
            tooltip=item["name"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(travel_map)
        
    return travel_map


def create_mood_map(destinations_list, tiles="Google Roadmap"):
    map_args = _get_map_args(tiles)
    # Center map at [20, 0] with zoom_start=2 for a global view of recommendations
    travel_map = folium.Map(
        location=[20, 0],
        zoom_start=2,
        **map_args
    )
    for dest in destinations_list:
        lat = dest.get("lat")
        lon = dest.get("lon")
        name = dest.get("name", "Destination")
        vibe = dest.get("vibe_class", "")
        desc = dest.get("description", "")
        if lat is not None and lon is not None:
            popup_html = f"""
            <div style="font-family: sans-serif; color: #1E293B; width: 220px;">
                <h4 style="margin: 0 0 5px 0; color: #7C3AED;">📍 {name}</h4>
                <span style="font-size: 0.75rem; background: #EDE9FE; color: #6D28D9; padding: 2px 6px; border-radius: 4px; font-weight: bold; text-transform: uppercase;">{vibe}</span>
                <p style="margin: 8px 0 0 0; font-size: 0.85rem; line-height: 1.4;">{desc}</p>
            </div>
            """
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=name,
                icon=folium.Icon(color="purple", icon="cloud")
            ).add_to(travel_map)
    return travel_map


def create_hotel_map(center_lat, center_lon, center_name, hotels_list, tiles="Google Roadmap"):
    map_args = _get_map_args(tiles)
    travel_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        **map_args
    )
    
    # Highlight main center location
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>City Center: {center_name}</b>",
        tooltip=center_name,
        icon=folium.Icon(color="red", icon="star")
    ).add_to(travel_map)
    
    # Mark all hotels
    for item in hotels_list:
        lat = item.get("lat")
        lon = item.get("lon")
        if lat is not None and lon is not None:
            name = item.get("name", "Hotel")
            price = item.get("price_range", "N/A")
            rating = item.get("rating", "N/A")
            htype = item.get("type", "Boutique")
            desc = item.get("description", "")
            popup_html = f"""
            <div style="font-family: sans-serif; color: #1E293B; width: 220px;">
                <h4 style="margin: 0 0 5px 0; color: #10B981;">🏨 {name}</h4>
                <span style="font-size: 0.75rem; background: #D1FAE5; color: #065F46; padding: 2px 6px; border-radius: 4px; font-weight: bold;">★ {rating} | {htype}</span>
                <div style="margin: 5px 0; font-size: 0.85rem; font-weight: bold; color: #059669;">{price}</div>
                <p style="margin: 5px 0 0 0; font-size: 0.8rem; line-height: 1.4; color: #4B5563;">{desc}</p>
            </div>
            """
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=name,
                icon=folium.Icon(color="green", icon="home")
            ).add_to(travel_map)
            
    return travel_map