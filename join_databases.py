import sqlite3
import pandas as pd
from datetime import datetime

def connect_to_databases():
    """Connect to all three databases and return their connections"""
    bts_conn = sqlite3.connect('bts_data/bts_data.db')
    opsnet_conn = sqlite3.connect('opsnet_data/opsnet_data.db')
    weather_conn = sqlite3.connect('weather/weather_data.db')
    return bts_conn, opsnet_conn, weather_conn

def load_data(bts_conn, opsnet_conn, weather_conn):
    """Load data from all databases into pandas DataFrames"""
    # Load BTS data with unique flight identifiers
    bts_df = pd.read_sql_query("""
        SELECT FL_DATE, 
               OP_UNIQUE_CARRIER,
               OP_CARRIER_AIRLINE_ID,
               ORIGIN, DEST, 
               DEP_DELAY, ARR_DELAY, 
               DEP_DEL15, ARR_DEL15
               CANCELLED, CARRIER_DELAY, WEATHER_DELAY, NAS_DELAY, SECURITY_DELAY
               ORIGIN_AIRPORT_ID, DEST_AIRPORT_ID,
               ORIGIN_CITY_NAME, DEST_CITY_NAME
        FROM bts_data
    """, bts_conn)
    
    # Load OPSNET data
    opsnet_df = pd.read_sql_query("""
        SELECT Date, Facility, "Total Operations" as total_ops
        FROM opsnet_table
    """, opsnet_conn)
    
    # Load weather data
    weather_df = pd.read_sql_query("""
        SELECT airport, 
               year, month, day,
               temperature_2m_max,
               precipitation_sum,
               wind_speed_10m_max
        FROM weather
    """, weather_conn)
    
    return bts_df, opsnet_df, weather_df

def prepare_data(bts_df, opsnet_df, weather_df):
    """Prepare and clean the data for joining"""
    # Convert dates to consistent format
    bts_df['FL_DATE'] = pd.to_datetime(bts_df['FL_DATE'])
    opsnet_df['Date'] = pd.to_datetime(opsnet_df['Date'])
    
    # Create date column in weather_df
    weather_df['date'] = pd.to_datetime(
        weather_df[['year', 'month', 'day']]
    )
    
    # Create unique flight identifier
    bts_df['flight_id'] = bts_df.apply(
        lambda x: f"{x['FL_DATE']}_{x['OP_UNIQUE_CARRIER']}_{x['ORIGIN']}_{x['DEST']}", 
        axis=1
    )
    
    # Create origin and destination specific weather conditions
    weather_orig = weather_df.copy()
    weather_dest = weather_df.copy()
    
    return bts_df, opsnet_df, weather_orig, weather_dest

def join_databases(bts_df, opsnet_df, weather_orig, weather_dest):
    """Join all databases together"""
    # First join BTS with origin weather
    merged_df = pd.merge(
        bts_df,
        weather_orig,
        left_on=['FL_DATE', 'ORIGIN'],
        right_on=['date', 'airport'],
        how='left',
        suffixes=('', '_origin')
    )
    
    # Join with destination weather
    merged_df = pd.merge(
        merged_df,
        weather_dest,
        left_on=['FL_DATE', 'DEST'],
        right_on=['date', 'airport'],
        how='left',
        suffixes=('', '_dest')
    )
    
    # Join with OPSNET data for origin airport
    merged_df = pd.merge(
        merged_df,
        opsnet_df,
        left_on=['FL_DATE', 'ORIGIN'],
        right_on=['Date', 'Facility'],
        how='left',
        suffixes=('', '_origin')
    )
    
    # Join with OPSNET data for destination airport
    merged_df = pd.merge(
        merged_df,
        opsnet_df,
        left_on=['FL_DATE', 'DEST'],
        right_on=['Date', 'Facility'],
        how='left',
        suffixes=('', '_dest')
    )
    
    # Drop redundant columns
    cols_to_drop = ['date', 'airport', 'Date', 'Facility', 
                    'date_dest', 'airport_dest', 'Date_dest', 'Facility_dest',
                    'year', 'month', 'day', 'year_dest', 'month_dest', 'day_dest']
    merged_df = merged_df.drop(columns=[col for col in cols_to_drop if col in merged_df.columns])
    
    return merged_df

def main():
    # Connect to databases
    bts_conn, opsnet_conn, weather_conn = connect_to_databases()
    
    try:
        # Load data from all databases
        print("Loading data from databases...")
        bts_df, opsnet_df, weather_df = load_data(bts_conn, opsnet_conn, weather_conn)
        
        # Prepare data for joining
        print("Preparing data...")
        bts_df, opsnet_df, weather_orig, weather_dest = prepare_data(bts_df, opsnet_df, weather_df)
        
        # Join databases
        print("Joining databases...")
        final_df = join_databases(bts_df, opsnet_df, weather_orig, weather_dest)
        
        # Save the joined data
        print("Saving joined data...")
        final_df.to_csv('joined_flight_data.csv', index=False)
        print(f"Successfully joined databases! Output saved to joined_flight_data.csv")
        print(f"Final dataset shape: {final_df.shape}")
        
        # Display sample of joined data and unique flight count
        print("\nSample of joined data:")
        print(final_df.head())
        print(f"\nNumber of unique flights: {final_df['flight_id'].nunique()}")
        
    finally:
        # Close connections
        bts_conn.close()
        opsnet_conn.close()
        weather_conn.close()

if __name__ == "__main__":
    main() 
