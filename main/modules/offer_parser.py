# modules/offer_parser.py

from bs4 import BeautifulSoup

class Offer:
    def __init__(self):
        self.origin_airport = ""
        self.destination_airport = ""
        self.outbound_date = ""
        self.outbound_departure_time = ""
        self.outbound_price = ""
        self.inbound_date = ""
        self.inbound_departure_time = ""
        self.inbound_price = ""

def parse_offer(result):
    # Parse HTML to extract offer details
    # Create and return an Offer object
    offer = Offer()
    
    text_div = result.find('div', class_='text')
    if text_div:
        detail_lines = text_div.find_all('p')
        if len(detail_lines) >= 3:
            # Parse outbound details
            outbound = detail_lines[0]
            
            aero_details = outbound.find_all('span', class_='aeroDetail')
            
            if len(aero_details) > 0:
                offer.origin_airport = aero_details[0].get_text()
            
                # TODO: 
                dest = outbound.find('span', class_='to').get_text().split()[1]
                
                offer.destination_airport = dest

                #offer.destination_airport = outbound.find('span', class_='to').find('span', class_='aeroDetail').get_text()
                
                offer.outbound_date = outbound.find('span', class_='date').get_text()
                offer.outbound_departure_time = outbound.find('span', class_='from').find('strong').get_text()
                offer.outbound_price = outbound.find('span', class_='subPrice').get_text()

                # Parse inbound details
                inbound = detail_lines[2]
                offer.inbound_date = inbound.find('span', class_='date').get_text()
                offer.inbound_departure_time = inbound.find('span', class_='from').find('strong').get_text()
                offer.inbound_price = inbound.find('span', class_='subPrice').get_text()

    return offer
