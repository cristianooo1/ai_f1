import fastf1
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(CACHE_DIR, exist_ok=True)

# !!!!!enable cache to AVOID REDOWNLOADING the data everytime the script is ran!!!!!!!
fastf1.Cache.enable_cache(CACHE_DIR)

def test_api_connection():

    # load a race from 2025 as test
    session = fastf1.get_session(2025, '5', 'R')
    session.load()
    
    winner = session.results.iloc[0]
    fastest_lap = session.laps.pick_fastest()
    
    print(f"Race Winner: {winner['FirstName']} {winner['LastName']} ({winner['TeamName']})")
    print(f"Fastest Lap: {fastest_lap['Driver']} - {fastest_lap['LapTime']}")

if __name__ == "__main__":
    test_api_connection()