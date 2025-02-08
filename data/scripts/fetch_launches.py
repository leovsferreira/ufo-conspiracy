import requests
import json
import os

# ============================================================
# SETUP: Define output directory relative to this script
# ============================================================
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# File to store launches data along with the last offset
DATA_FILE = os.path.join(OUTPUT_DIR, "spacedevs_launches.json")

def load_existing_data(file_path):
    """
    Load existing launch data if the file exists.
    
    The file is expected to be a JSON object with keys:
      - "offset": the last offset reached
      - "results": a list of launch records fetched so far.
    
    Returns:
      (offset, results) tuple. If file doesn't exist, returns (0, []).
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return data.get("offset", 0), data.get("results", [])
    else:
        return 0, []

def save_data(file_path, offset, results):
    """
    Save the current offset and results to a JSON file.
    """
    data = {
        "offset": offset,
        "results": results
    }
    # No spaces, no identation
    with open(file_path, "w") as f:
        json.dump(data, f, separators=(',', ':'))

def fetch_launches_thespacedevs():
    """
    Fetches launch data from The Space Devs API (dev endpoint) using pagination.
    
    Process:
      - Uses the endpoint "https://ll.thespacedevs.com/2.3.0/launches/".
      - Requests 100 records per call and increases the offset by 100.
      - Resumes from where the last fetch ended if data already exists.
      - Continues fetching until fewer than 100 records are returned.
      - Saves the updated data (including current offset and results) to the output file.
    
    Output:
      - A JSON file named "spacedevs_launches.json" in OUTPUT_DIR containing the launches data.
    """
    base_url = "https://ll.thespacedevs.com/2.3.0/launches/"
    limit = 100

    # Load existing data if available
    offset, all_launches = load_existing_data(DATA_FILE)
    print(f"Resuming from offset {offset}. Already fetched {len(all_launches)} records.")

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
        
        # Append the new launches to our list
        all_launches.extend(results)
        
        # Increase offset by limit
        offset += limit
        
        # Save the updated data to file after each successful call (so we don't lose progress)
        save_data(DATA_FILE, offset, all_launches)
        print(f"Saved data up to offset {offset}. Total records: {len(all_launches)}")
        
        # If fewer than the limit are returned, then we've reached the end.
        if len(results) < limit:
            print("Fetched last page of results.")
            break
    
    print("🚀 Launches from The Space Devs API captured!")
    
if __name__ == "__main__":
    fetch_launches_thespacedevs()