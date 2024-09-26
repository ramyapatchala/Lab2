import requests
import streamlit as st

def get_current_weather(location, API_key):
    if "," in location:
        location = location.split(",")[0].strip()
      
    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={API_key}"
    url = urlbase + urlweather
    response = requests.get(url)
    data = response.json()
    # Extract temperatures & Convert Kelvin to Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']
    return {
        "location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2)
    }

st.title("Current Weather App")

# Input field for location without default value
location = st.text_input("Enter a location (city name):")

# Button to trigger weather fetch
if st.button("Get Weather"):
    if location:  # Check if location is not empty
        api_key = st.secrets["OpenWeatherAPIkey"]
        try:
            weather_data = get_current_weather(location, api_key)
            st.write(f"Current weather in {weather_data['location']}:")
            st.write(f"Temperature: {weather_data['temperature']}°C")
            st.write(f"Feels like: {weather_data['feels_like']}°C")
            st.write(f"Min temperature: {weather_data['temp_min']}°C")
            st.write(f"Max temperature: {weather_data['temp_max']}°C")
            st.write(f"Humidity: {weather_data['humidity']}%")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a location.")
