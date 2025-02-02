from datetime import datetime
import requests
from typing import Optional

class NotionSyringeManager:
    def __init__(self, notion_token: str, dosage_db_id: str, status_db_id: str):
        """Initialize the Notion Syringe Manager.
        
        Args:
            notion_token: Notion API integration token
            dosage_db_id: ID of the dosage log database
            status_db_id: ID of the syringe status database
        """
        self.notion_token = notion_token
        self.dosage_db_id = dosage_db_id
        self.status_db_id = status_db_id
        self.headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"

    def get_syringe(self) -> Optional[dict]:
        """Retrieve the current amount of the active syringe.
        
        Returns:
            dict: Syringe information including current amount and ID,
                 or None if no active syringe is found
        """
        # Query the status database for the active syringe
        query_url = f"{self.base_url}/databases/{self.status_db_id}/query"
        filter_data = {
            "filter": {
                "property": "status",
                "select": {
                    "equals": "IN_USE"
                }
            }
        }
        
        response = requests.post(query_url, headers=self.headers, json=filter_data)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if not results:
            return None
        
        syringe = results[0]
        return {
            "syringe_id": syringe["id"],
            "current_amount": syringe["properties"]["current_amount"]["number"],
            "initial_amount": syringe["properties"]["initial_amount"]["number"],
            "opening_date": syringe["properties"]["opening_date"]["date"]["start"]
        }

    def take_dose(self, amount: float = 0.75) -> bool:
        """Record a new dose event and update the syringe status.
        
        Args:
            amount: Amount of medication taken (default: 0.75ml)
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            requests.exceptions.HTTPError: If the Notion API request fails
        """
        # Get current syringe status
        syringe = self.get_syringe()
        if not syringe or syringe["current_amount"] < amount:
            return False
        
        # Create new dose log entry
        now = datetime.utcnow().isoformat()
        create_page_url = f"{self.base_url}/pages"
        
        dose_data = {
            "parent": {"database_id": self.dosage_db_id},
            "properties": {
                "amount": {"number": amount},
                "date_taken": {"date": {"start": now}},
                "syringe_id": {"rich_text": [{"text": {"content": syringe["syringe_id"]}}]},
                "clicks": {"number": 1}  # Assuming one click per dose
            }
        }
        
        # Create dose log entry
        response = requests.post(create_page_url, headers=self.headers, json=dose_data)
        response.raise_for_status()
        
        # Update syringe status
        new_amount = syringe["current_amount"] - amount
        update_url = f"{self.base_url}/pages/{syringe['syringe_id']}"
        
        update_data = {
            "properties": {
                "current_amount": {"number": new_amount},
                "last_update": {"date": {"start": now}}
            }
        }
        
        response = requests.patch(update_url, headers=self.headers, json=update_data)
        response.raise_for_status()
        
        return True

# Example usage:
if __name__ == "__main__":
    # Initialize with your Notion credentials
    notion_manager = NotionSyringeManager(
        notion_token=os.getenv("NOTION_API_KEY"),
        dosage_db_id="your_dosage_db_id",
        status_db_id="your_status_db_id"
    )
    
    # Get current syringe status
    syringe = notion_manager.get_syringe()
    if syringe:
        print(f"Current amount: {syringe['current_amount']}ml")
    
    # Take a dose
    if notion_manager.take_dose():
        print("Dose recorded successfully")
    else:
        print("Failed to record dose - insufficient amount or no active syringe")