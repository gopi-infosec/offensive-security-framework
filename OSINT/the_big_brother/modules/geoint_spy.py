import requests

def get_geoint_data(lat: str, lon: str):
    """
    Generates a GEOINT package for the given coordinates.
    Includes Sat links, SunCalc, and search queries for social media.
    """
    try:
        f_lat = float(lat)
        f_lon = float(lon)
    except:
        return {"error": "Invalid coordinates"}

    # Google Maps URL
    gmaps = f"https://www.google.com/maps/place/{f_lat},{f_lon}/@{f_lat},{f_lon},18z/data=!3m1!1e3"
    
    # Street View
    street = f"https://www.google.com/maps?layer=c&cbll={f_lat},{f_lon}"
    
    # SunCalc (Shadow Analysis)
    suncalc = f"https://www.suncalc.org/#/{f_lat},{f_lon},18/now"
    
    # Tweet Locator (Twitter advanced search near location)
    # geocode:LAT,LONG,RADIUS
    twitter = f"https://twitter.com/search?q=geocode%3A{f_lat}%2C{f_lon}%2C1km&src=typed_query&f=live"
    
    # Snapchat Map
    snapchat = f"https://map.snapchat.com/@{f_lat},{f_lon},15.00z"
    
    # Wikimapia
    wikimapia = f"http://wikimapia.org/#lang=en&lat={f_lat}&lon={f_lon}&z=18&m=b"

    return {
        "coords": f"{f_lat}, {f_lon}",
        "links": {
            "Google Satellite": gmaps,
            "Street View": street,
            "SunCalc (Shadows)": suncalc,
            "Twitter (Nearby)": twitter,
            "Snapchat Map": snapchat,
            "Wikimapia": wikimapia
        }
    }
