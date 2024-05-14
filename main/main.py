import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options  # Import Options
import telebot
from modules import offer_parser, telegram_notifier
from datetime import date
import calendar
from selenium import webdriver
from selenium.webdriver.common.by import By

# Constants
URL = "https://www.azair.eu/"
# TODO: make token an environment variable
# BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = 324109540
YEAR = 2024

# Set up Chrome Options
options = Options()
options.add_argument("--ignore-certificate-errors")  # Add this line to ignore SSL errors
options.add_argument("--headless")  # Optional: Run Chrome in headless mode (without GUI)

# Initialize bot
BOT = telebot.TeleBot("6824381438:AAFaoV_9QF8trD56obqJL5BsPSDY3xMG_8o")

# Set up the Selenium WebDriver with Chrome Options
driver = webdriver.Chrome(options=options)

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
                    weekends.append((start_day.day, day.day))
                    start_day = None
                
    return weekends

def initialize_driver(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver                

def scrape_results(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def parse_results(soup):
    results = soup.find_all('div', class_='result')
    return results

def send_notification(offer):
    # Implement your notification logic here
    pass

def main():    
    driver = initialize_driver(URL)
    
    # tick the checkbox "take me anywhere"
    take_me_anywhere = driver.find_element(By.CSS_SELECTOR, "input[name='anywhere']")
    take_me_anywhere.click()
           
    # parse and work with the search page                        
    get_url = driver.current_url
    page = requests.get(get_url)
    soup = BeautifulSoup(page.content, 'html5lib')
    
    # get list of distinct months concatenated with the (current) YEAR, e.g. 202406
    distinct_month_list = get_distinct_months()
    print(distinct_month_list)
    
    # get all weekend dates (+- 1 day) in the current month
    weekends = get_weekends()
    print(weekends)
    
    # find 'departure month' date selector and set the month
    depmonth_tag = soup.find('select', {'name' : 'depmonth'})
    option_value = distinct_month_list[1]
    option_tag = depmonth_tag.find('option', {'value': option_value})
    print(option_tag)
    
    # TODO: set month and dates 
    
    # simulate 'Search' button click
    send_button = driver.find_element(By.CSS_SELECTOR, "input[class='bt blue']")
    send_button.click()

    # parse result page
    soup = scrape_results(driver.current_url)
    results = soup.find_all('div', class_='result')
    
    for result in results:
        offer = offer_parser.parse_offer(result)
        telegram_notifier.send_notification(offer, BOT, CHAT_ID)
        
        # TODO: make sure to send an offer once
        # this can be achieved by storing them in the database 
    
    # Close the browser
    driver.quit()


if __name__ == "__main__":
    main()