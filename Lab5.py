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

# Streamlit Weather App Interface
st.title("Current Weather App")

# Input field for location with "Syracuse, NY" as the default value
location = st.text_input("Enter a location (city name):", value="Syracuse, NY")

# Button to trigger weather fetch
if st.button("Get Weather"):
    if location:
        try:
            # Prepare prompt for OpenAI to fetch weather and suggest clothing/picnic advice
            prompt = (f"Get the current weather for {location} in Celsius. "
                      "Then provide advice on what to wear and whether it's a good day for a picnic.")
            
            # Create messages for chat completion request
            messages = [{"role": "user", "content": prompt}]
            
            # Call OpenAI API for the weather and suggestions using tools
            response = chat_completion_request(messages, tools=tools)
            
            # Display the response content
            st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a location.")
