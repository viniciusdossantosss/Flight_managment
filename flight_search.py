import os
import requests
from dotenv import load_dotenv

load_dotenv()


class FlightSearch:
    def __init__(self):
        self._api_key = os.environ["SERPAPI_API_KEY"]
        self.base_url = "https://serpapi.com/search"

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time):
        query_params = {
            "engine": "google_flights",
            "departure_id": origin_city_code,
            "arrival_id": destination_city_code,
            "outbound_date": from_time,
            "return_date": to_time,
            "type": "1",
            "adults": "1",
            "currency": "BRL",
            "api_key": self._api_key,
        }

        response = requests.get(url=self.base_url, params=query_params)

        if response.status_code != 200:
            print(f"Erro na SerpAPI: Status {response.status_code}")
            print(response.text)
            return None

        return response.json()