import sqlite3
from weather_data import airport_weather_query

iata_codes = set()

def set_airplane_information():
    iata_codes.update( {
    "ATL", "AUS", "BWI", "BOS", "CLT", "MDW", "ORD", "DFW", "DEN", "DTW", 
    "FLL", "IAH", "LAS", "LAX", "MIA", "MSP", "BNA", "JFK", "LGA", "EWR", 
    "MCO", "PHL", "PHX", "SLC", "SAN", "SFO", "SEA", "TPA", "DCA", "IAD"
    })

    return iata_codes

def grab_lat_lon_data(airports):

    db_path = "/Users/alexanderadams/Downloads/global_airports_sqlite.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ", ".join("?" for _ in airports)

    query = f'''
            SELECT lat_decimal, lon_decimal
            FROM airports 
            WHERE iata_code IN ({placeholders})
            '''
    
    cursor.execute(query, airports)
    results = cursor.fetchall()

    conn.close()

    
    return dict(zip(iata_codes, results))
    


if __name__ == "__main__":
    airplane_codes = tuple(set_airplane_information())
    airport_dict = grab_lat_lon_data(airplane_codes)
    airport_data = airport_weather_query(airport_dict)

    airport_data.to_csv("airport_weather_data.csv", index=False)
