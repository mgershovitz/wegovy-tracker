import requests
import json
from datetime import datetime

# Notion API settings
NOTION_API_URL = "https://api.notion.com/v1/pages"
DATABASE_ID_DOSAGE_LOG = "your_dosage_log_database_id"  # Replace with your actual Dosage Log database ID
DATABASE_ID_SYRINGE_STATUS = "your_syringe_status_database_id"  # Replace with your actual Syringe Status database ID
NOTION_TOKEN = "your_notion_integration_token"  # Replace with your actual Notion API token
NOTION_VERSION = "2021-05-13"  # The Notion API version

# Headers for Notion API requests
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

# Function to send the dosage event to the Dosage Log
def TakeDose(amount_taken, syringe_id):
    """
    Adds a new dosage event to the Dosage Log table in Notion.
    """
    # Construct the data payload for the new event
    data = {
        "parent": {"database_id": DATABASE_ID_DOSAGE_LOG},
        "properties": {
            "Amount": {
                "number": amount_taken  # Amount of liquid taken (e.g., 0.75 ml)
            },
            "Clicks": {
                "number": 1  # Assuming one click is a single dose
            },
            "Date Taken": {
                "date": {
                    "start": datetime.utcnow().isoformat()  # The current UTC date and time
                }
            },
            "Syringe ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": syringe_id  # Syringe ID from the Syringe Status table
                        }
                    }
                ]
            }
        }
    }

    # Make the API request to Notion to create the new event
    response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(f"Successfully logged dose of {amount_taken} ml for Syringe ID {syringe_id}")
    else:
        print(f"Failed to log dose: {response.status_code} - {response.text}")

# Function to get the current syringe amount for the syringe with status 'IN_USE'
def GetSyringe():
    """
    Retrieves the current syringe amount for the syringe with the status 'IN_USE'.
    """
    # Query the Syringe Status table for the syringe with status 'IN_USE'
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID_SYRINGE_STATUS}/query"
    query = {
        "filter": {
            "property": "Status",
            "select": {
                "equals": "IN_USE"
            }
        }
    }

    # Make the API request to Notion to query the Syringe Status database
    response = requests.post(url, headers=headers, data=json.dumps(query))

    if response.status_code == 200:
        # Get the syringe that is 'IN_USE'
        data = response.json()
        if data["results"]:
            syringe = data["results"][0]  # Get the first syringe found (should be the only one with 'IN_USE')
            syringe_id = syringe["id"]
            current_amount = syringe["properties"]["Current Amount"]["number"]
            print(f"Current Syringe Amount for Syringe ID {syringe_id}: {current_amount} ml")
            return current_amount
        else:
            print("No syringe is currently marked as IN_USE.")
            return None
    else:
        print(f"Failed to retrieve syringe: {response.status_code} - {response.text}")
        return None
