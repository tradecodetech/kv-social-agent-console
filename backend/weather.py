import requests

def get_weather_summary(lat=33.5779, lon=-101.8552):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,precipitation_sum"
        "&timezone=auto"
    )

    data = requests.get(url, timeout=10).json()
    temp = data["daily"]["temperature_2m_max"][0]
    rain = data["daily"]["precipitation_sum"][0]

    if rain > 5:
        return "wet conditions"
    if temp > 90:
        return "heat stress"
    return "normal conditions"
