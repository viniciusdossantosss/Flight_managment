# Flight Deal Finder and Alert System
#### Video Demo: <https://youtu.be/SEU-VIDEO-AQUI>
#### Description:

For my CS50P final project, I built a Python program that helps me find cheap flights. Instead of manually checking flight prices every day, this program does the work for me and sends me an SMS alert if it finds a good deal.

Here is how it works: I have a Google Sheet where I list the cities I want to travel and the maximum price I am willing to pay for a ticket. The program reads this spreadsheet, searches for flights over the next six months using Google Flights data, and compares the prices. If it finds a flight that is cheaper than my target price, it sends me a text message with the details so I can book it right away.

### Project Structure

I decided to put all the main code into a single file, `project.py`, to keep things simple and meet the course requirements. Here is a breakdown of what is inside:

1. **`project.py`**: This is the heart of the project. Inside, you will find:
   - The `main()` function, which runs the whole process step-by-step.
   - Three functions (`check_price_lower`, `format_flight_message`, and `parse_flight_data`) that I wrote so I could easily test the logic with `pytest`.
   - The `DataManager` class, which talks to the Sheety API to read my target prices from Google Sheets.
   - The `FlightSearch` class, which uses the SerpAPI to pull real flight data from Google Flights.
   - The `FlightData` class, a simple structure to hold the flight details like the origin, destination, dates, and price.
   - The `NotificationManager` class, which connects to the Twilio API to send the actual SMS messages to my phone.

2. **`test_project.py`**: I wrote this file to test the three helper functions. It makes sure that the program correctly identifies when a price is lower, formats the text message properly, and extracts the right data from the API response. You can run these tests using `pytest`.

3. **`requirements.txt`**: This file lists the external Python libraries my project needs, like `requests` for making API calls and `twilio` for sending texts.

### Design Choices

This design choices are from a course that I made and never finished, it's a project from 100 days of Python from Angela Yu, of couse are choices that I made, to make this project more simple like not using a whatsapp message, and just the method get from sheety.

- **Caching**: API limits are the cause of this choice, I only used free subscriptions. I used the `requests-cache` library with an SQLite database to save the API responses for an hour. This way, I do not waste my free API credits while running the script multiple times.
- **Security**: I did not want to hardcode my API keys or my phone number directly into the code. Instead, I used the `python-dotenv` library to load them securely from a `.env` file.
- **Testing without the Internet**: The tests used only offline data, this was designed to not depend of internet to do the tests, and the internet data change every time because of the flight prices.

### How to Run It

1. First, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a file named `.env` in the same folder and add your API credentials like this:
   ```text
   SHEETY_PRICES_ENDPOINT="your_sheety_url"
   SHEETY_TOKEN="your_sheety_token"
   SERPAPI_API_KEY="your_serpapi_key"
   TWILIO_SID="your_twilio_sid"
   TWILIO_AUTH_TOKEN="your_twilio_auth_token"
   TWILIO_VIRTUAL_NUMBER="your_twilio_number"
   TWILIO_VERIFIED_NUMBER="your_real_phone_number"
   ```
   *(You will need to create free accounts on Sheety, SerpAPI, and Twilio to get these keys).*
3. Run the program:
   ```bash
   python project.py
   ```
4. Or, run the tests:
   ```bash
   pytest test_project.py
   ```
