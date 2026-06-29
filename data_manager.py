import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DataManager:
    def __init__(self):
        self.endpoint = os.environ.get("SHEETY_PRICES_ENDPOINT")
        self.headers = {
            "Authorization": os.environ.get("SHEETY_TOKEN"),
            "Content-Type": "application/json",
        }
        self.destination_data = {}

    def get_destination_data(self):
        response = requests.get(url=self.endpoint, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            self.destination_data = data["prices"]
            return self.destination_data
        else:
            print(f"Error reading Sheety: {response.status_code} - {response.reason}")
            return []

    def update_destination_iata(self, row_id, iata_code):
        update_url = f"{self.endpoint}/{row_id}"

        body = {
            "price": {
                "iataCode": iata_code
            }
        }

        response = requests.put(
            url=update_url,
            json=body,
            headers=self.headers
        )
        if response.status_code == 200:
            print(f"Row {row_id} updated with success to IATA code: {iata_code}!")
        else:
            print(f"Fail to update row {row_id}: {response.status_code}")