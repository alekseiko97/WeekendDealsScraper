# modules/offer_parser.py

class Offer:
    def __init__(self):
        self.origin_airport = ""
        self.destination_airport = ""
        self.outbound_date = ""
        self.outbound_departure_time = ""
        self.outbound_arrival_time = "" # TODO
        self.outbound_price = ""
        self.inbound_date = ""
        self.inbound_departure_time = ""
        self.inbound_arrival_time = "" # TODO
        self.inbound_price = ""
        self.total_price = 0.0

def parse_offer(result):
    try:
        # Parse HTML to extract offer details
        # Create and return an Offer object
        offer = Offer()
        
        text_div = result.find('div', class_='text')
        
        if text_div:
            detail_lines = text_div.find_all('p')
            if len(detail_lines) >= 3:
                outbound = detail_lines[0]

                offer.origin_airport = outbound.find('span', class_='from').get_text().split()[1]
                offer.destination_airport = outbound.find('span', class_='to').get_text().split()[1] # Also contains time, therefore [1]

                # Parse inbound details
                for p in detail_lines:
                    there = p.find('span', class_='caption tam')
                    if there:
                        outbound = there.find_parent('p')
                        if outbound:
                            # Outbound
                            offer.outbound_date = outbound.find('span', class_='date').get_text()
                            offer.outbound_departure_time = outbound.find('span', class_='from').find('strong').get_text()
                            offer.outbound_price = outbound.find('span', class_='subPrice').get_text()
                                
                    # Parse outbound details
                    for p in detail_lines:
                        back = p.find('span', class_='caption sem')
                        if back:
                            inbound = back.find_parent('p')
                            if inbound:
                                # Inbound
                                offer.inbound_date = inbound.find('span', class_='date').get_text()
                                offer.inbound_departure_time = inbound.find('span', class_='from').find('strong').get_text()
                                offer.inbound_price = inbound.find('span', class_='subPrice').get_text()
                    
                    # Calculate total price (return)
                    total_price = float(offer.outbound_price.strip("€")) + float(offer.inbound_price.strip("€"))
                    offer.total_price = total_price
                    
                    return offer
            else:
                print("Insufficient detail lines for offer")
        else:
            print("Text div not found for offer")
    except Exception as error:
        print("An expection occurred while parsing offer: ", error)
 
    return None   