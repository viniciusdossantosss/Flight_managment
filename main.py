#This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.
import requests_cache
from data_manager import DataManager
from pprint import pprint
from flight_search import FlightSearch
from datetime import datetime, timedelta

requests_cache.install_cache(
    'flight_cache',
    backend='sqlite',
    expire_after=3600)

data_manager = DataManager()

planilha_de_dados = data_manager.get_destination_data()

flight_search = FlightSearch()

today = datetime.now()
tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
six_month_from_today = (today + timedelta(days=6 * 30)).strftime("%Y-%m-%d")

print(f"Buscando voos de LHR para CDG de {tomorrow} até {six_month_from_today}...")
dados_voo = flight_search.check_flights(
    origin_city_code="LHR",
    destination_city_code="CDG",
    from_time=tomorrow,
    to_time=six_month_from_today
)
# Imprime o resultado formatado no console
if dados_voo:
    print("\n================== RESULTADO DA SERPAPI ==================")
    pprint(dados_voo)