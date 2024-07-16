import requests
import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options  # Import Options
import telebot
from modules import offer_parser, telegram_notifier, MockOffer
from datetime import date
import calendar
from selenium import webdriver
from urllib.parse import urlparse, parse_qs, urlencode
import pandas as pd
from openpyxl.workbook import Workbook
import streamlit as st
import logging
import requests
import json
import aiohttp
import asyncio
from streamlit_dynamic_filters import DynamicFilters
from concurrent.futures import ThreadPoolExecutor
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('myLogger')

# Constants
URL = "https://www.azair.eu/azfin.php"
# TODO: make token an environment variable
# BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_TOKEN = "6824381438:AAFaoV_9QF8trD56obqJL5BsPSDY3xMG_8o"
CHAT_ID = 324109540
YEAR = 2024

# Initialize bot
BOT = telebot.TeleBot(BOT_TOKEN)

def get_distinct_months(current_date=date.today(), num_months=12):
    distinct_months = set()  # Using a set to store unique month+YEAR combinations
    current_month = current_date.month  # Get the current month
    
    for _ in range(num_months):
        if current_month > 12:
            current_month -= 12  # Adjust month if it exceeds 12
        
        # Create a string representing the month and YEAR, e.g., "202405"
        month_year = f"{current_date.year}{current_month:02d}"
        
        # Check if the month is equal to or after the current month
        if int(month_year) >= int(current_date.strftime("%Y%m")):
            distinct_months.add(month_year)  # Add the month+YEAR combination to the set
        
        current_month += 1  # Move to the next month
    
    # Convert the set to a list and sort it to ensure the months are in ascending order
    return sorted(list(distinct_months))


def get_weekends(month=date.today().month):
    """
    Get weekends for a given month.
    :param month: Month for which to get weekends.
    :return: List of tuples with start and end dates for weekends.
    """
    weekends = []
    c = calendar.TextCalendar(calendar.MONDAY)
    
    days = c.itermonthdays(YEAR, month)
    start_day = None
    
    for i in days: # calendar constructs months with leading zeros (days belonging to the previous month)
        if i != 0:
            day = date(YEAR, month, i)
            if day >= date.today() and (day.weekday() == 0 or day.weekday() == 4): # Friday to Monday
                if start_day is None:
                    start_day = day
                elif day.weekday() == 0: # Monday
                    start_date = start_day.strftime("%Y%m%d")
                    end_date = day.strftime("%Y%m%d")
                    weekends.append((start_date, end_date))
                    start_day = None
                
    return weekends           

def scrape_flight_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        flight_details = soup.find_all('div', class_='result')
        return flight_details
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return None
    

def parse_flight_details(soup):
    flight_details = soup.find_all('div', class_='result')
    return flight_details

async def fetch_price(session, url, params):
    async with session.get(url, params=params) as response:
        response.raise_for_status()
        data = await response.json()
        if 'fares' in data and isinstance(data['fares'], list) and len(data['fares']):
            if 'outbound' in data['fares'][0] and 'price' in data['fares'][0]['outbound']:
                return data['fares'][0]['outbound']['price']['value']
        return None

# TODO: compare parsed price from Azair with the price obtained through Ryanair API (if it's Ryanair airline)
async def get_leg_price_from_ryanair_api(offers):
    url = 'https://services-api.ryanair.com/farfnd/3/oneWayFares'
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for offer in offers:
            date = datetime.datetime.strptime(offer.outbound_date.split()[1], '%d/%m/%y').strftime('%Y-%m-%d')

            # Define the parameters
            params = {
                'departureAirportIataCode': offer.origin_airport_code,
                'arrivalAirportIataCode': offer.destination_airport_code,
                'language': 'en',
                'market': 'en-gb',
                'offset': 0,
                'outboundDepartureDateFrom': date,
                'outboundDepartureDateTo': date
            }
            tasks.append(fetch_price(session, url, params))
        return await asyncio.gather(*tasks)

# TODO: check the price prediction on airhint 
def buy_or_wait(offer):
    pass

def update_params(params, depdate, arrdate):
    params["depdate"] = depdate
    params["arrdate"] = arrdate
    return URL + "?" + urlencode(params)

def process_weekends(weekends, original_params):
    results = []
    offers = []
    for date_range in weekends:
        updated_url = update_params(original_params.copy(), date_range[0], date_range[1])
        flight_details = scrape_flight_details(updated_url)
        # If there is anything to be parse
        if (flight_details):
            for detail in flight_details:
                offer = offer_parser.parse_offer(detail)
                if offer:
                    offers.append(offer)
        
        if offers:
            ryanair_prices = asyncio.run(get_leg_price_from_ryanair_api(offers))            
                    
            for i, offer in enumerate(offers):
                ryanair_outbound_price = ryanair_prices[i] if offer.outbound_airline == "Ryanair" else None        
                    
                results.append({
                        'Departure Date': offer.outbound_date,
                        'Outbound Departure Time': offer.outbound_departure_time,
                        'Outbound Airline': offer.outbound_airline,
                        'Outbound Price (Azair)': offer.outbound_price,
                        'Ryanair Outbound Actual Price (if applicable)': ryanair_outbound_price,  # Make sure you have this variable if used
                        
                        'Arrival Date': offer.inbound_date,
                        'Inbound Departure Time': offer.inbound_departure_time,
                        'Inbound Airline': offer.inbound_airline,
                        'Inbound Price (Azair)': offer.inbound_price,
                        'Ryanair Inbound Actual Price (if applicable)': None,  # Make sure you have this variable if used
                        
                        'Origin': offer.origin_airport,
                        'Origin airport code': offer.origin_airport_code,
                        'Destination': offer.destination_airport,
                        'Destination airport code': offer.destination_airport_code,
                        'Total Price': offer.total_price
                    })
    
    return results


# entry point
def main():    
    st.title("Flight results")
    
    # Original query parameters
    original_params = {
        "searchtype": "flexi",
        "tp": "0",
        "isOneway": "return",
        "srcAirport": "Amsterdam [AMS] (+EIN,NRN,BRU,DUS,CRL)",
        "srcap0": "EIN",
        "srcap1": "NRN",
        "srcap2": "BRU",
        "srcap4": "DUS",
        "srcap6": "CRL",
        "srcFreeAirport": "",
        "srcTypedText": "amsterda",
        "srcFreeTypedText": "",
        "srcMC": "",
        "dstAirport": "Anywhere [XXX]",
        "anywhere": "true",
        "dstTypedText": "anywhere",
        "dstFreeTypedText": "",
        "dstMC": "",
        "depmonth": "202405",
        "depdate": "2024-05-17",
        "aid": "0",
        "arrmonth": "202405",
        "arrdate": "2024-05-20",
        "minDaysStay": "2",
        "maxDaysStay": "4",
        "dep4": "true",
        "dep5": "true",
        "arr0": "true",
        "arr6": "true",
        "wizzxclub": "true",
        "minHourStay": "0:45",
        "maxHourStay": "23:20",
        "minHourOutbound": "0:00",
        "maxHourOutbound": "24:00",
        "minHourInbound": "0:00",
        "maxHourInbound": "24:00",
        "autoprice": "true",
        "adults": "1",
        "children": "0",
        "infants": "0",
        "maxChng": "1",
        "currency": "EUR",
        "lang": "en",
        "indexSubmit": "Search"
    }
    
    # get all weekend dates (+- 1 day) in the current month
    weekends = get_weekends()
    print(weekends)
    
    # Create a list to store the results
    results = process_weekends(weekends, original_params)
    
    # Convert results list to DataFrame
    results_df = pd.DataFrame(results)    

    file_path = 'flight_results.xlsx'
                    
    # Save results to Excel file
    results_df.to_excel(file_path, index=False, header=True)
    
    dynamic_filters = DynamicFilters(df=results_df, filters=['Outbound Airline'])
    
    dynamic_filters.display_filters()
    # Display results in web using streamlit 
    dynamic_filters.display_df()
    
    # Indicate that the file has been created
    logger.info(f"File '{file_path}' has been created successfully.")

# entry point
if __name__ == "__main__":
    main()