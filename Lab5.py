import requests
import streamlit as st
import openai

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

client = openai.OpenAI(api_key=st.secrets["key1"])

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
                        "enum": ['celsius', 'fahrenheit'],
                        "description": "The temperature unit to use. Infer this from the user's location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
]

def chat_completion_request(messages, tools=None):
    try:
        params = {
            "model": "gpt-4",
            "messages": messages,
        }
        if tools:
            params["functions"] = tools
            params["function_call"] = "auto"
        
        response = client.chat_completions.create(**params)
        return response
    except Exception as e:
        st.error(f"Unable to generate ChatCompletion response: {e}")
        return None

st.title("Weather Chatbot with Suggestions")

location = st.text_input("Enter a location (city name):", "Syracuse, NY")

if st.button("Get Weather and Suggestions"):
    if location:
        api_key = st.secrets["OpenWeatherAPIkey"]
        
        # Initial message to the chatbot
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides weather information and suggestions."},
            {"role": "user", "content": f"What's the weather like in {location} today? Based on the weather, what clothes should I wear and is it a good day for a picnic?"}
        ]
        
        # First API call to get weather data
        chat_response = chat_completion_request(messages, tools=tools)
        if chat_response:
            assistant_message = chat_response["choices"][0]["message"]
            messages.append(assistant_message)
            
            # Check if the assistant is requesting weather data
            if "function_call" in assistant_message:
                function_call = assistant_message["function_call"]
                
                if function_call["name"] == "get_current_weather":
                    # Get actual weather data
                    weather_data = get_current_weather(location, api_key)
                    
                    # Provide weather data to the assistant, making sure to include the tool_call_id
                    messages.append({
                        "role": "function",
                        "name": "get_current_weather",
                        "tool_call_id": function_call["id"],  # Associate response with the tool call
                        "content": str(weather_data)
                    })
                    
                    # Second API call to get suggestions
                    final_response = chat_completion_request(messages)
                    if final_response:
                        suggestion = final_response["choices"][0]["message"]["content"]
                        st.write(suggestion)
                    else:
                        st.error("Failed to get suggestions.")
                else:
                    st.error(f"Unexpected function call: {function_call['name']}")
            else:
                st.write(assistant_message["content"])
        else:
            st.error("Failed to communicate with the chatbot.")
    else:
        st.warning("Please enter a location.")
