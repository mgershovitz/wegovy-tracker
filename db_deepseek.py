import os
import requests
import json
from datetime import datetime

# Constants
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DOSAGE_LOG_DATABASE_ID = os.getenv("SYRINGE_STATUS_DB")
SYRINGE_STATUS_DATABASE_ID = os.getenv("SYRINGE_STATUS_DB")
NOTION_API_URL = "https://api.notion.com/v1"

# Headers for Notion API requests
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",  # Use the latest Notion API version
}

def TakeDose(amount_taken: float, syringe_id: str):
    """
    Adds a new dose event to the Dosage Log table in Notion.
    
    Args:
        amount_taken (float): The amount of liquid taken in ml.
        syringe_id (str): The ID of the syringe used.
    """
    # Create the payload for the new dose event
    payload = {
        "parent": {"database_id": DOSAGE_LOG_DATABASE_ID},
        "properties": {
            "Amount": {"number": amount_taken},
            "Date Taken": {"date": {"start": datetime.now().isoformat()}},
            "Syringe ID": {"rich_text": [{"text": {"content": syringe_id}}]},
        },
    }

    # Send the request to Notion API
    response = requests.post(
        f"{NOTION_API_URL}/pages",
        headers=HEADERS,
        data=json.dumps(payload),
    )

    if response.status_code == 200:
        print("Dose logged successfully!")
    else:
        print(f"Failed to log dose: {response.status_code}, {response.text}")

def GetSyringe():
    """
    Retrieves the current amount of the syringe with status IN_USE from the Syringe Status table.
    
    Returns:
        float: The current amount of liquid in the syringe.
    """
    # Query the Syringe Status table to find the syringe with status IN_USE
    query_payload = {
        "filter": {
            "property": "Status",
            "status": {"equals": "IN_USE"},
        }
    }

    response = requests.post(
        f"{NOTION_API_URL}/databases/{SYRINGE_STATUS_DATABASE_ID}/query",
        headers=HEADERS,
        data=json.dumps(query_payload),
    )

    if response.status_code != 200:
        print(f"Failed to query syringe status: {response.status_code}, {response.text}")
        return None

    # Parse the response
    data = response.json()
    results = data.get("results", [])

    if not results:
        print("No syringe with status IN_USE found.")
        return None

    # Get the first syringe (assuming only one syringe is IN_USE)
    syringe = results[0]
    current_amount = syringe["properties"]["CurrentAmount"]["number"]
    print("found syringe")
    print(current_amount)

    return current_amount

# Example Usage
if __name__ == "__main__":
    # Get the current amount in the syringe
    current_amount = GetSyringe()
    if current_amount is not None:
        print(f"Current amount in syringe: {current_amount} ml")

        # Take a dose (0.75 ml) and log it
        TakeDose(amount_taken=0.75, syringe_id="your_syringe_id")