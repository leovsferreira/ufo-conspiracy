import requests
import json
import os

# ============================================================
# SETUP: Define output directory relative to this script
# ============================================================
# Get the absolute path of the directory this script is in.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the output directory (for example, one level up in a folder named "raw").
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "raw")
# Create the output directory if it doesn't already exist.
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_launches_thespacedevs():
    """
    Fetches launch data from The Space Devs API (dev endpoint) with no query limit (though it has less data).
    
    Process:
      - Uses the endpoint "https://lldev.thespacedevs.com/2.3.0/launches/".
      - Sets limit=100 per request and increases offset by 100 for each call.
      - Continues fetching until fewer than 100 records are returned.
      - Saves the cleaned data to a JSON file called "spacedevs_launches.json" in OUTPUT_DIR.
    
    Output:
      - A JSON file containing the launch data.
    """
    base_url = "https://lldev.thespacedevs.com/2.3.0/launches/"
    limit = 100
    offset = 0
    all_launches = []
    
    while True:
        params = {
            "limit": limit,
            "offset": offset
        }
        print(f"Fetching launches with offset {offset}...")
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print("Error fetching data:", response.status_code)
            break
        
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No more results. Finishing up!")
            break
        
        # Loop over each launch and extract key fields.
        for launch in results:
            all_launches.append(launch)
            # Save the cleaned launches data to a JSON file with no extra spaces
        output_file = os.path.join(OUTPUT_DIR, "spacedevs_launches.json")

        # If fewer than the limit are returned, we've reached the end.
        if len(results) < limit:
            break
        offset += limit
    
    # Save the cleaned launches data to a JSON file with no extra spaces
    output_file = os.path.join(OUTPUT_DIR, "spacedevs_launches.json")
    with open(output_file, "w") as f:
        json.dump(all_launches, f, separators=(',', ':'))
    
    print("🚀 Launches from The Space Devs API captured!")
    
if __name__ == "__main__":
    fetch_launches_thespacedevs()