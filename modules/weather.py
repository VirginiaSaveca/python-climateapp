# modules/weather.py
import requests

API_KEY = '8a4128baab6cde739906b46b6f81200d'  # Substitua pela sua chave da API do WeatherAPI

def get_weather_data(city):
    url = f'https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data['current']['temp_c']
        humidity = data['current']['humidity']
        condition = data['current']['condition']['text']
        
        return {
            'temperature': temperature,
            'humidity': humidity,
            'condition': condition
        }
    else:
        print("Erro ao buscar dados:", response.status_code)
        return None

