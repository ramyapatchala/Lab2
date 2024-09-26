import requests
import streamlit as st
import openai

# Define the tools as described
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ['celcius', 'fahrenheit'],
                        "description": "The temperature unit to use. Infer this from the user's location.",
                    },
                },
                "required": ["location", "format"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day Weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Syracuse, NY",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celcius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from user's location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    },
                },
                "required": ["location", "format", "num_days"],
            },
        }
    }
]

client = openai.OpenAI(api_key=st.secrets["key1"])
# Function for OpenAI chat completion requests
def chat_completion_request(messages, tools, tool_choice=None):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        return response
    except Exception as e:
        st.error(f"Unable to generate ChatCompletion response. Error: {e}")
        return e

# Weather data function
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

# Streamlit Weather App Interface
st.title("Current Weather App")

# Input field for location without default value
location = st.text_input("Enter a location (city name):")

# Button to trigger weather fetch
if st.button("Get Weather"):
    if location:
        api_key = st.secrets["OpenWeatherAPIkey"]
        try:
            # Fetch and display weather data
            weather_data = get_current_weather(location, api_key)
            st.write(f"Current weather in {weather_data['location']}:")
            st.write(f"Temperature: {weather_data['temperature']}°C")
            st.write(f"Feels like: {weather_data['feels_like']}°C")
            st.write(f"Min temperature: {weather_data['temp_min']}°C")
            st.write(f"Max temperature: {weather_data['temp_max']}°C")
            st.write(f"Humidity: {weather_data['humidity']}%")

            # Prepare prompt for OpenAI to suggest clothing and picnic advice
            prompt = (f"The weather in {weather_data['location']} is {weather_data['temperature']}°C "
                      f"with a feels-like temperature of {weather_data['feels_like']}°C, "
                      f"and a humidity of {weather_data['humidity']}%. "
                      "What should I wear today and is it a good day for a picnic?")
            
            # OpenAI request for clothing and picnic suggestion
            messages = [{"role": "user", "content": prompt}]
            response = chat_completion_request(messages, tools = tools)

            st.write(response.choices[0].message["content"])

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a location.")
