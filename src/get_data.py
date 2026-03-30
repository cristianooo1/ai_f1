import fastf1
import os
import sys  

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(CACHE_DIR, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)

def download_entire_season(year=2025):
    schedule = fastf1.get_event_schedule(year)
    official_races = schedule[schedule['RoundNumber'] > 0]
    
    print(f"Found {len(official_races)} race weekends.\n")
    
    for index, event in official_races.iterrows():
        round_num = event['RoundNumber']
        event_name = event['EventName']
        
        print(f"####################### Downloading Round {round_num}: {event_name} ######################################")
        
        for session_num in range(1, 6):
            try:
                session = fastf1.get_session(year, round_num, session_num)
                session.load()
                print(f"  ✅ SUCCESDULLY loaded: {session.name}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ FAILED loading session {session_num}. Error: {error_msg}")
                
                # check if it is the rate limit error
                if "500 calls/h" in error_msg:
                    print("\n API RATE LIMIT REACHED (500 calls/hour)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    sys.exit() 
        print("\n")

if __name__ == "__main__":
    download_entire_season(2025)