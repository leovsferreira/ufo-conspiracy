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

def fetch_spacex_launches():
    """
    Fetches SpaceX launch data from the SpaceX API (v4) and saves it as a cleaned JSON file.

    Process:
        - Sends a GET request to the SpaceX API to retrieve all launches.
        - Extracts key fields from each launch, including date, launchpad ID, rocket ID,
          success status, and details.
        - Saves the cleaned data to a JSON file in the specified output directory.

    Output:
        - A JSON file named `spacex_launches.json` containing the cleaned launch data.
    """
    # URL endpoint for SpaceX launches (v4 of the API)
    url = "https://api.spacexdata.com/v4/launches"
    
    # Send a GET request to fetch the launches data
    response = requests.get(url)
    
    # Parse the response as JSON (a list of launch dictionaries)
    launches = response.json()
    
    # Create an empty list to store our cleaned-up launch data
    clean_launches = []
    
    # Loop over each launch in the data
    for launch in launches:
        # For each launch, extract only the key fields we're interested in.
        # These fields are:
        #   - date: when the launch happened (UTC)
        #   - launchpad_id: the identifier for the launchpad used
        #   - rocket_id: the identifier for the rocket
        #   - success: whether the launch was successful or not
        #   - details: additional text details (if any)
        clean_launches.append({
            "date": launch["date_utc"],
            "launchpad_id": launch["launchpad"],
            "rocket_id": launch["rocket"],
            "success": launch["success"],
            "details": launch["details"]
        })
    
    # Build the absolute path to the output JSON file and save (no spaces, no identation)
    output_file = os.path.join(OUTPUT_DIR, "spacex_launches.json")
    with open(output_file, "w") as f:
        json.dump(clean_launches, f, separators=(',', ':'))
    
    print("🚀 SpaceX launches captured!")

def fetch_spacex_launchpads():
    """
    Fetches SpaceX launchpad data from the SpaceX API (v4) and saves it as a cleaned JSON file.

    Process:
        - Sends a GET request to the SpaceX API to retrieve all launchpads.
        - Extracts key fields from each launchpad, including name, full name, locality,
          region, timezone, rockets list, launches list, and ID.
        - Saves the cleaned data to a JSON file in the specified output directory.

    Output:
        - A JSON file named `spacex_launchpads.json` containing the cleaned launchpad data.
    """
    # URL endpoint for SpaceX launches (v4 of the API)
    url = "https://api.spacexdata.com/v4/launchpads"
    
    # Send a GET request to fetch the launchpads data
    response = requests.get(url)
    
    # Parse the response as JSON (a list of launch dictionaries)
    launchpads = response.json()
    
    # Create an empty list to store our cleaned-up launch data
    clean_launchpads = []
    
    # Loop over each launchpad in the data
    for launchpad in launchpads:
        # For each launch, extract only the key fields we're interested in.
        # These fields are:
        #   - name: location abbreviation
        #   - full_name: location full name
        #   - locality: location short name
        #   - region: state
        #   - timezone: location timezone
        #   - rockets: list of rockets
        #   - launches: list of launches in the current location
        #   - id: launchpad id
        clean_launchpads.append({
            "name": launchpad["name"],
            "full_name": launchpad["full_name"],
            "locality": launchpad["locality"],
            "region": launchpad["region"],
            "timezone": launchpad["timezone"],
            "rockets_list": launchpad["rockets"],
            "launches_list": launchpad["launches"],
            "id": launchpad["id"]
        })
    
    # Build the absolute path to the output JSON file and save (no spaces, no identation)
    output_file = os.path.join(OUTPUT_DIR, "spacex_launchpads.json")
    with open(output_file, "w") as f:
        json.dump(clean_launchpads, f, separators=(',', ':'))
    
    print("🚀 SpaceX launchpads captured! (Elon, if you're reading this, we come in peace.)")

if __name__ == "__main__":
    fetch_spacex_launches()
    fetch_spacex_launchpads()