# modules/offer_parser.py

class Offer:
    def __init__(self):
        self.origin_airport = ""
        self.origin_airport_code = "" # TODO
        self.destination_airport = "" 
        self.destination_airport_code = "" # TODO
        self.outbound_date = ""
        self.outbound_departure_time = ""
        self.outbound_arrival_time = "" # TODO
        self.outbound_price = ""
        self.outbound_airline = "" # TODO
        self.inbound_date = ""
        self.inbound_departure_time = ""
        self.inbound_arrival_time = "" # TODO
        self.inbound_price = ""
        self.inbound_airline = "" # TODO
        self.total_price = 0.0

def parse_offer(result):
    try:
        # Parse HTML to extract offer details
        # Create and return an Offer object
        offer = Offer()
        
        text_div = result.find('div', class_='text')
        
        details = result.find_all('div', class_='detail')
        
        outbound_details = details[0].find('p')
        inbound_details = details[1].find('p')
        
        if text_div:
            detail_lines = text_div.find_all('p')
            if len(detail_lines) >= 3:
                outbound = detail_lines[0]

                offer.origin_airport = outbound.find('span', class_='from').get_text().split()[1]
                offer.destination_airport = outbound.find('span', class_='to').get_text().split()[1] # Also contains time, therefore [1]

                # Parse outbound details
                for p in detail_lines:
                    there = p.find('span', class_='caption tam')
                    if there:
                        outbound = there.find_parent('p')
                        if outbound:
                            # Outbound
                            offer.outbound_date = outbound.find('span', class_='date').get_text()
                            offer.outbound_departure_time = outbound.find('span', class_='from').find('strong').get_text()
                            offer.destination_airport_code = outbound.find('span', class_='to').find('span', class_='code').contents[0].strip()
                            if outbound.find('span', class_='from').find('span', class_='code'):
                                offer.origin_airport_code = outbound.find('span', class_='from').find('span', class_='code').contents[0].strip()
                            offer.outbound_price = outbound.find('span', class_='subPrice').get_text()
                            offer.outbound_airline = outbound_details.find('span', class_='airline').get_text()
                                
                    # Parse inbound details
                    for p in detail_lines:
                        back = p.find('span', class_='caption sem')
                        if back: 
                            inbound = back.find_parent('p')
                            if inbound:
                                # Inbound
                                offer.inbound_date = inbound.find('span', class_='date').get_text()
                                offer.inbound_departure_time = inbound.find('span', class_='to').get_text()[0]
                                offer.inbound_price = inbound.find('span', class_='subPrice').get_text()
                                offer.inbound_airline = inbound_details.find('span', class_='airline').get_text()
                    
                    # Calculate total price (return)
                    total_price = float(offer.outbound_price.strip("€")) + float(offer.inbound_price.strip("€"))
                    offer.total_price = total_price
                    
                    return offer
            else:
                # TODO: add logging
                print("Insufficient detail lines for offer")
        else:
            print("Text div not found for offer")
    except Exception as error:
        print("An expection occurred while parsing offer: ", error)
 
    return None   