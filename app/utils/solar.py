import requests

def get_monthly_ghi(lat, lon, month_abbr):
    """
    Returns long-term monthly average GHI (kWh/m²/day) for a given lat/lon and month.
    Example: get_monthly_ghi(29.8323, -95.7785, 'JAN')
    """
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=CLRSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}&format=JSON"

    try:
        response = requests.get(url)
        data = response.json()
        ghi = data["properties"]["parameter"]["CLRSKY_SFC_SW_DWN"].get(month_abbr.upper())
        return round(ghi, 2) if ghi else None
    except Exception as e:
        print(f"Error fetching GHI: {e}")
        return None
