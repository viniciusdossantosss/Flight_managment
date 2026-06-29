class FlightData:
    def __init__(self, price, origin_airport, destination_airport, out_date, return_date):
        self.price = price
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date


def find_cheapest_flight(data, return_date):

    if not data or ("best_flights" not in data and "other_flights" not in data):
        print("Nenhum dado de voo válido foi recebido da API.")
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")

    all_flights = data.get("best_flights", []) + data.get("other_flights", [])

    if not all_flights:
        print("Nenhum voo disponível para este destino no período selecionado.")
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")


    cheapest_flight_obj = None

    for flight in all_flights:
        try:
            if "price" not in flight:
                continue

            current_price = flight["price"]

            if cheapest_flight_obj is None or current_price < cheapest_flight_obj.price:
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