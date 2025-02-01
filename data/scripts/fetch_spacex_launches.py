import requests
import json

def fetch_spacex_launches():
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
    
    # Save the cleaned list of launches to a JSON file.
    # Make sure the folder "../data/raw/" exists, otherwise you'll get an error.
    with open("../raw/spacex_launches.json", "w") as f:
        json.dump(clean_launches, f)
    
    print("🚀 SpaceX launches captured! (Elon, if you're reading this, we come in peace.)")

if __name__ == "__main__":
    fetch_spacex_launches()