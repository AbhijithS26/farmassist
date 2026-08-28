import requests
import json

def get_location():
    '''
    Get approximate latitude and longitude based on IP address using ipapi.co.
    Returns (latitude, longitude) or (None, None) if failed.
    '''
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            return latitude, longitude
        else:
            return None, None
    except Exception:
        return None, None

def get_weather(latitude, longitude):
    '''
    Fetch current weather data for given latitude and longitude using Open-Meteo API.
    Returns a human-readable string describing the weather.
    '''
    try:
        # Open-Meteo API endpoint for current weather
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current_weather': True,
            'hourly': 'temperature_2m,relativehumidity_2m,precipitation,weathercode,windspeed_10m',
            'timezone': 'auto'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'current_weather' not in data:
            return 'Weather data not available.'

        current = data['current_weather']
        temp = current.get('temperature')
        windspeed = current.get('windspeed')
        weathercode = current.get('weathercode')
        time = current.get('time')

        # Weather code mapping (simplified)
        weather_code_descriptions = {
            0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
            45: 'Fog', 48: 'Depositing rime fog', 51: 'Light drizzle', 53: 'Moderate drizzle',
            55: 'Dense drizzle', 56: 'Light freezing drizzle', 57: 'Dense freezing drizzle',
            61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain', 66: 'Light freezing rain',
            67: 'Heavy freezing rain', 71: 'Slight snow fall', 73: 'Moderate snow fall',
            75: 'Heavy snow fall', 77: 'Snow grains', 80: 'Slight rain showers',
            81: 'Moderate rain showers', 82: 'Violent rain showers', 85: 'Slight snow showers',
            86: 'Heavy snow showers', 95: 'Thunderstorm', 96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }

        description = weather_code_descriptions.get(weathercode, f'Weather code {weathercode}')

        # Build readable string
        weather_str = f'Current weather (as of {time}): {description}, Temperature: {temp}°C, '
        weather_str += f'Wind Speed: {windspeed} km/h'

        # Optionally add humidity and precipitation from hourly if available
        if 'hourly' in data:
            hourly = data['hourly']
            if 'relativehumidity_2m' in hourly and hourly['relativehumidity_2m']:
                # Get the most recent humidity value (index 0 if current)
                humidity = hourly['relativehumidity_2m'][0] if hourly['relativehumidity_2m'] else None
                if humidity is not None:
                    weather_str += f', Humidity: {humidity}%'
            if 'precipitation' in hourly and hourly['precipitation']:
                precip = hourly['precipitation'][0] if hourly['precipitation'] else None
                if precip is not None:
                    weather_str += f', Precipitation: {precip} mm'

        return weather_str
    except Exception as e:
        return f'Error fetching weather data: {str(e)}'

if __name__ == '__main__':
    # Example usage (latitude/longitude for Chennai, India)
    lat = 13.0827
    lon = 80.2707
    print(get_weather(lat, lon))

