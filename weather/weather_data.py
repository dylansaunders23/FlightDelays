import openmeteo_requests
import sqlite3
import requests_cache
import pandas as pd
from pandas import DataFrame as df
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

def create_weather_database():
    conn = sqlite3.connect('weather_database.db')
    cursor = conn.cursor()




def airport_weather_query(airport_data):
    all_airport_weather = []

    for airport, coordinates in airport_data.items():
        two_year_weather_data = query_weather(coordinates)
        print(two_year_weather_data)
        # Convert to DataFrame
        df = pd.DataFrame(two_year_weather_data)
        
        # Add airport identifier
        df["airport"] = airport
        
        # Append to list
        all_airport_weather.append(df)

    # Concatenate all DataFrames into one
    final_df = pd.concat(all_airport_weather, ignore_index=True)
    
    return final_df

def query_weather(coordinates):
    params = {
        "latitude": coordinates[0],
        "longitude": coordinates[1],
        "start_date": "2022-11-01",
        "end_date": "2024-11-30",
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_hours", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
    daily_showers_sum = daily.Variables(4).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(5).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(6).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(7).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(8).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(9).ValuesAsNumpy()
    daily_wind_direction_10m_dominant = daily.Variables(10).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["showers_sum"] = daily_showers_sum
    daily_data["snowfall_sum"] = daily_snowfall_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours
    daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
    daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

    return daily_data



