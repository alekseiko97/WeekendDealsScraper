# Weekend Deals Scraper

## Overview

This Python script scrapes flight deals from azair.eu, storing the best weekend getaway deals (Friday - Monday) in an Excel file. Additionally, it sends a notification to a Telegram chat bot upon successful parsing completion. Future enhancements will include setting up a cron process to execute the script periodically and transitioning towards a web solution using streamlit and a database.

## Features

- Scraping and parsing flight deals from azair.eu using BeautifulSoup4.
- Comparing parsed prices from azair with Ryanair (other airlines support to be added later) by utilizing Ryanair API 
- Storing parsed results in an Excel file.
- Displaying results on a web page using streamlit library, with the possibility to dynamically filter data
- **TODO:** Implementing a cron job for periodic execution.
- **TODO:** Sending a notification to a Telegram chatbot upon successful parsing completion. 
- **TODO:** Possibility to monitor certain flights' prices change using airhint.com

## Requirements

- Python 3.x
- `requests` library
- `beautifulsoup4` library
- `pandas` library
- `openpyxl` library
- `python-telegram-bot` library
- `streamlit` library
- `streamlit_dynamic_filters`
- `aiohttp`
- `asyncio`

## Installation

Install the required libraries using pip:

```bash
pip install requests beautifulsoup4 pandas openpyxl python-telegram-bot streamlit
```

## Usage

1. **Configure the Script**

   Update the `params` dictionary in the script to match your search requirements on azair.eu. For example:

   ```python
   params = {
       'searchtype': 'flexi',
       'flexibility': '2',
       'departure': 'NYC',
       'destination': '',
       'adults': '1',
       'children': '0',
       'infants': '0',
       'minhours': '0',
       'maxhours': '48',
       'minprice': '0',
       'maxprice': '200',
       'direct': 'on',
       'minhourstop': '0',
       'maxhourstop': '12',
       'mindeparture': '06:00',
       'maxdeparture': '20:00',
       'mindepartureback': '10:00',
       'maxdepartureback': '23:00',
       'depdate': '2024-06-01',
       'arrdate': '2024-06-03'
   }

2. **Run the Script**

   Execute the script to start scraping and saving the results:

   ```bash
   python weekend_deals_scraper.py
   ```

   To be able to visualize the data on a web page and possibly apply filters, execute the following command:
   
   ```bash
   streamlit run .\main\main.py
   ```

3. **Check the Results**

   The results will be stored in an Excel file in the same directory as the script.

   For the web solution, the script will be executed locally on http://localhost:8501/ (unless another port is specified)
