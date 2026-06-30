from project import check_price_lower, format_flight_message, parse_flight_data, FlightData


def test_check_price_lower():
    # Preço menor → deve retornar True
    assert check_price_lower(150, 200) is True
    assert check_price_lower(0, 100) is True

    # Preço maior ou igual → deve retornar False
    assert check_price_lower(250, 200) is False
    assert check_price_lower(200, 200) is False

    # Valores inválidos → deve retornar False sem erro
    assert check_price_lower("N/A", 200) is False
    assert check_price_lower(150, "N/A") is False
    assert check_price_lower(None, 200) is False
    assert check_price_lower(None, None) is False


def test_format_flight_message():
    message = format_flight_message(100, "LHR", "CDG", "2026-07-01", "2026-12-31")
    assert "Low price alert!" in message
    assert "£100" in message
    assert "LHR" in message
    assert "CDG" in message
    assert "from 2026-07-01 to 2026-12-31" in message

    # Verifica que funciona com outros destinos
    message2 = format_flight_message(599, "GRU", "HND", "2026-08-15", "2026-09-15")
    assert "£599" in message2
    assert "GRU" in message2
    assert "HND" in message2


def test_parse_flight_data():
    # Resposta válida com um voo
    mock_api_response = {
        "best_flights": [
            {
                "price": 150,
                "flights": [
                    {
                        "departure_airport": {"id": "LHR", "time": "2026-07-01 10:00"},
                        "arrival_airport": {"id": "CDG", "time": "2026-07-01 12:00"}
                    }
                ]
            }
        ]
    }
    flight = parse_flight_data(mock_api_response, "2026-12-31")
    assert isinstance(flight, FlightData)
    assert flight.price == 150
    assert flight.origin_airport == "LHR"
    assert flight.destination_airport == "CDG"
    assert flight.out_date == "2026-07-01"
    assert flight.return_date == "2026-12-31"

    # Resposta vazia → deve retornar FlightData com "N/A"
    flight_vazio = parse_flight_data({}, "2026-12-31")
    assert flight_vazio.price == "N/A"

    # Resposta None → deve retornar FlightData com "N/A"
    flight_none = parse_flight_data(None, "2026-12-31")
    assert flight_none.price == "N/A"
