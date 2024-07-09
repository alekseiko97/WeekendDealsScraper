import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options  # Import Options
import telebot
from modules import offer_parser, telegram_notifier
from datetime import date
import calendar
from selenium import webdriver
from urllib.parse import urlparse, parse_qs, urlencode
import pandas as pd
from openpyxl.workbook import Workbook
import streamlit as st

# Constants
URL = "https://www.azair.eu/azfin.php"
# TODO: make token an environment variable
# BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = 324109540
YEAR = 2024

# Set up Chrome Options
# options = Options()
#options.add_argument("--ignore-certificate-errors")  # Add this line to ignore SSL errors
# options.add_argument("--headless")  # Optional: Run Chrome in headless mode (without GUI)
# Set up the Selenium WebDriver with Chrome Options
# driver = webdriver.Chrome(options=options)

# Initialize bot
BOT = telebot.TeleBot("6824381438:AAFaoV_9QF8trD56obqJL5BsPSDY3xMG_8o")

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
    response = requests.get(url)
    if response.status_code == 200: # OK
        soup = BeautifulSoup(response.content, 'html.parser')
        flight_details = soup.find_all('div', class_='result')
        return flight_details
    else:
        print("Error:", response.status_code)
        return None
    

def parse_flight_details(soup):
    flight_details = soup.find_all('div', class_='result')
    return flight_details

def send_notification(offer):
    # Implement your notification logic here
    pass

# TODO: compare parsed price from Azair with the price obtained through Ryanair API (if it's Ryanair airline)
def get_leg_price_from_ryanair(price):
    pass

# entry point
def main():    
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
    
    # get list of distinct months concatenated with the (current) YEAR, e.g. 202406
    #distinct_month_list = get_distinct_months()
    #print(distinct_month_list)
    
    # get all weekend dates (+- 1 day) in the current month
    weekends = get_weekends()
    print(weekends)
    
    # Create a list to store the results
    results = []
    
    for date_range in weekends:
            # Update departure and arrival dates in query parameters
            params = original_params.copy()
            params["depdate"] = date_range[0]
            params["arrdate"] = date_range[1]
            
            # Construct URL with updated parameters
            updated_url = URL + "?" + urlencode(params)
            
            # Scrape result page
            flight_details = scrape_flight_details(updated_url)
            
            if flight_details:
                for detail in flight_details:
                    offer = offer_parser.parse_offer(detail)
                    if offer is not None:
                        results.append({'Departure Date' : offer.outbound_date, 'Outbound Departure Time': offer.outbound_departure_time, 'Arrival Date' : offer.inbound_date, 'Inbound Departure Time': offer.inbound_departure_time, 'Origin': offer.origin_airport, 'Destination': offer.destination_airport, 'Total Price': offer.total_price})
                
    # Convert results list to DataFrame
    results_df = pd.DataFrame(results)    

    file_path = 'flight_results.xlsx'
                    
    # Save results to Excel file
    results_df.to_excel(file_path, index=False, header=True)
    
    results_df
    
    # Indicate that the file has been created
    print(f"File '{file_path}' has been created successfully.")
    #telegram_notifier.send_notification(file_path, BOT, CHAT_ID)
    
    # for result in flight_details:
    #     offer = offer_parser.parse_offer(result)
        
    #     # TODO: generate an Excel file containing flight offers and notify with a single message in Telegram bot
        
    #     if offer is not None:
    #         telegram_notifier.send_notification(offer, BOT, CHAT_ID)
            
    #         break
        
    #     # TODO: make sure to send an offer once
    #     # this can be achieved by storing them in the database 


if __name__ == "__main__":
    main()