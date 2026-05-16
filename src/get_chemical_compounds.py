import requests
from bs4 import BeautifulSoup
import re
import time

# list of 2025 races
races = [
    "Australian_Grand_Prix", "Chinese_Grand_Prix", "Japanese_Grand_Prix",
    "Bahrain_Grand_Prix", "Saudi_Arabian_Grand_Prix", "Miami_Grand_Prix",
    "Emilia_Romagna_Grand_Prix", "Monaco_Grand_Prix", "Spanish_Grand_Prix",
    "Canadian_Grand_Prix", "Austrian_Grand_Prix", "British_Grand_Prix",
    "Belgian_Grand_Prix", "Hungarian_Grand_Prix", "Dutch_Grand_Prix",
    "Italian_Grand_Prix", "Azerbaijan_Grand_Prix", "Singapore_Grand_Prix",
    "United_States_Grand_Prix", "Mexico_City_Grand_Prix", "São_Paulo_Grand_Prix",
    "Las_Vegas_Grand_Prix", "Qatar_Grand_Prix", "Abu_Dhabi_Grand_Prix"
]

compound_pattern = re.compile(r'\b(C[1-6])\b')

headers = {
    'User-Agent': 'F1TyreScraper/1.0 (Mozilla/5.0; Python requests)'
}


for race in races:
    url = f"https://en.wikipedia.org/wiki/2025_{race}"
    display_name = race.replace("_", " ")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"[{display_name}] Page not found or incomplete (Status: {response.status_code})")
            continue
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        paragraphs = soup.find_all('p')
        found_compounds = set()
        
        for p in paragraphs:
            text = p.get_text()
            if 'Pirelli' in text and ('tyre' in text.lower() or 'tire' in text.lower()):
                matches = compound_pattern.findall(text)
                if matches:
                    found_compounds.update(matches)
        
        if found_compounds:
            sorted_compounds = sorted(list(found_compounds))
            print(f"[{display_name}] Compounds: {', '.join(sorted_compounds)}")
        else:
            print(f"[{display_name}] No tyre data found on the page.")
            
    except Exception as e:
        print(f"[{display_name}] Error scraping: {e}")
        
    time.sleep(1)

print("\n SCRAPING COMPLETE!!!!!!!!!!!!!!!")