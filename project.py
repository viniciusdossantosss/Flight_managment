import os
import requests
import requests_cache
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


# ==================== CLASSES ====================


class FlightData:
    def __init__(self, price, origin_airport, destination_airport, out_date, return_date):
        self.price = price
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date


class DataManager:
    def __init__(self):
        self.endpoint = os.environ.get("SHEETY_PRICES_ENDPOINT", "")
        token = os.environ.get("SHEETY_TOKEN", "")
        self.headers = {
            "Authorization": token,
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
            print(f"SerpAPI Error: Status {response.status_code}")
            print(response.text)
            return None
        return response.json()


class NotificationManager:
    def __init__(self):
        self.client = Client(os.environ.get("TWILIO_SID", ""), os.environ.get("TWILIO_AUTH_TOKEN", ""))
        self.virtual_number = os.environ.get("TWILIO_VIRTUAL_NUMBER")
        self.verified_number = os.environ.get("TWILIO_VERIFIED_NUMBER")

    def send_sms(self, message_body):
        try:
            params = {
                "body": message_body,
                "to": self.verified_number
            }
            if self.virtual_number and self.virtual_number.startswith("MG"):
                params["messaging_service_sid"] = self.virtual_number
            else:
                params["from_"] = self.virtual_number

            message = self.client.messages.create(**params)
            print(f"SMS sent successfully! SID: {message.sid}")
        except Exception as e:
            print(f"Error sending SMS (check your Twilio credentials in .env): {e}")


# ==================== HELPER FUNCTIONS (testable with pytest) ====================

def check_price_lower(price, lowest_price):
    try:
        if price == "N/A" or price is None:
            return False
        return float(price) < float(lowest_price)
    except (ValueError, TypeError):
        return False


def format_flight_message(price, origin, destination, out_date, return_date):
    return (
        f"Low price alert! Only £{price} to fly from "
        f"{origin} to {destination}, "
        f"from {out_date} to {return_date}."
    )


def parse_flight_data(api_response: dict | None, return_date: str):
    if not api_response or ("best_flights" not in api_response and "other_flights" not in api_response):
        print("No valid flight data received from the API.")
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")

    all_flights = api_response.get("best_flights", []) + api_response.get("other_flights", [])

    if not all_flights:
        print("No flights available for this destination in the selected period.")
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")

    cheapest_flight_obj = None

    for flight in all_flights:
        try:
            if "price" not in flight:
                continue

            current_price = flight["price"]

            if cheapest_flight_obj is None or current_price < cheapest_flight_obj.price:  # noqa
                origin = flight["flights"][0]["departure_airport"]["id"]
                destination = flight["flights"][-1]["arrival_airport"]["id"]
                out_date = flight["flights"][0]["departure_airport"]["time"].split(" ")[0]

                cheapest_flight_obj = FlightData(
                    price=current_price,
                    origin_airport=origin,
                    destination_airport=destination,
                    out_date=out_date,
                    return_date=return_date
                )
        except (KeyError, IndexError):
            continue

    if cheapest_flight_obj is None:
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")

    return cheapest_flight_obj


# ==================== MAIN FUNCTION ====================

def main():
    requests_cache.install_cache(
        'flight_cache',
        backend='sqlite',
        expire_after=3600,
        urls_expire_after={
            'api.sheety.co': 0,
        }
    )

    data_manager = DataManager()
    flight_search = FlightSearch()
    notification_manager = NotificationManager()

    sheet_data = data_manager.get_destination_data()
    print("Current spreadsheet data:")
    print(sheet_data)

    today = datetime.now()
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    six_month_from_today = (today + timedelta(days=6 * 30)).strftime("%Y-%m-%d")

    if sheet_data:
        for destination in sheet_data:
            destination_code = destination.get("iataCode")
            destination_name = destination.get("city")
            current_lowest_price = destination.get("lowestPrice", float('inf'))

            if not destination_code:
                print(f"\nSkipping {destination_name}: IATA code missing.")
                continue

            print(f"\n--------------------------------------------------")
            print(f"Searching flights from SSA to {destination_name} ({destination_code}) from {tomorrow} to {six_month_from_today}...")

            flight_data = flight_search.check_flights(
                origin_city_code="SSA",
                destination_city_code=destination_code,
                from_time=tomorrow,
                to_time=six_month_from_today
            )

            if flight_data:
                cheapest_flight = parse_flight_data(flight_data, return_date=six_month_from_today)

                if cheapest_flight.price != "N/A":
                    print(f"Cheapest flight found for {destination_name}: {cheapest_flight.origin_airport} -> {cheapest_flight.destination_airport} for BRL {cheapest_flight.price} (Departure: {cheapest_flight.out_date})")
                    print(f"Spreadsheet price: BRL {current_lowest_price} | Found price: BRL {cheapest_flight.price}")

                    if check_price_lower(cheapest_flight.price, current_lowest_price):
                        print(f"Lower price found for {destination_name}! Sending notification...")

                        message = format_flight_message(
                            price=cheapest_flight.price,
                            origin=cheapest_flight.origin_airport,
                            destination=cheapest_flight.destination_airport,
                            out_date=cheapest_flight.out_date,
                            return_date=cheapest_flight.return_date
                        )
                        notification_manager.send_sms(message)
                    else:
                        print(f"Found price for {destination_name} is not lower than the current spreadsheet price.")
                else:
                    print(f"Could not find any valid flights for {destination_name}.")
            else:
                print(f"No response from search API for {destination_name}.")
    else:
        print("No destinations found in the spreadsheet to search.")


if __name__ == "__main__":
    main()
