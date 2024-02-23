import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options  # Import Options
import html5lib
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

    # Set up Chrome Options
options = Options()
options.add_argument("--ignore-certificate-errors")  # Add this line to ignore SSL errors
# options.add_argument("--headless")  # Optional: Run Chrome in headless mode (without GUI)

# Set up the Selenium WebDriver with Chrome Options
web_driver = webdriver.Chrome(options=options)
    
# web_driver = webdriver.Chrome("C:\\Users\\Aleksei\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")

class Offer:
    origin_airport = ""
    destination_airport = ""
    outbound_date = ""
    outbound_departure_time = 0
    outbound_changes = 0
    outbound_price = 0
    
    inbound_date = ""
    inbound_departure_time = 0
    inbound_changes = 0
    inbound_price = 0
    

def main():
    URL = "https://www.azair.eu/"
    
    web_driver.get(URL)
    
    # TODO: tweak input parameters
    
    send_button = web_driver.find_element(By.CSS_SELECTOR, "input[class='bt blue']")
    
    send_button.click()
    
    # page containing search results
    get_url = web_driver.current_url
    
    # parse result page
    page = requests.get(get_url)
    soup = BeautifulSoup(page.content, 'html5lib')
    
    # get the whole set of results
    soup.find('body', class_="results")
    
    # get specific results
    sections = soup.find_all('div', class_='result')
    
    prices = []
    for section in sections:
        offer = Offer()
        
        outbound_date = section.find('span', class_='date')
        
        print(f'outbound date: {outbound_date.get_text()}')
        
        departure_time = section.find('span', class_='from').find('strong')
        
        print (f'departure time: {departure_time.get_text()}')
        
        origin_airport = section.find('span', class_='code')
        
        print (f'origin airport code: {origin_airport.get_text()}')
        
        outbound_price = section.find('span', class_='subPrice')
        
        print(outbound_price.get_text())
        
        to = section.find('span', class_='to')
        
        print(to.get_text())
        
        print('-------------')
        print()
        
        
        
    
    
    # TODO: click on "Do not consent" button
    
    #print(soup.select('div.searchBox'))
    
    # Close the browser
    #web_driver.quit()
    # print [a.text for a in soup.select('div.searchBox')] 

if __name__ == "__main__":
    main()