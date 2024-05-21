# modules/offer_parser.py

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
    try:
        # Parse HTML to extract offer details
        # Create and return an Offer object
        offer = Offer()
        
        text_div = result.find('div', class_='text')
        
        if text_div:
            detail_lines = text_div.find_all('p')
            if len(detail_lines) >= 3:
                
                outbound = detail_lines[0]
                aero_details = outbound.find_all('span', class_='aeroDetail')
                
                if len(aero_details) > 0:
                    # Parse outbound details
                    offer.origin_airport = aero_details[0].get_text()
                    offer.destination_airport = outbound.find('span', class_='to').get_text().split()[1]
                    
                    offer.outbound_date = outbound.find('span', class_='date').get_text()
                    offer.outbound_departure_time = outbound.find('span', class_='from').find('strong').get_text()
                    offer.outbound_price = outbound.find('span', class_='subPrice').get_text()

                    # Parse inbound details
                    #inbound = detail_lines[2]

                    # Find the span with class 'caption sem'
                    #span_caption_sem = detail_lines.find('span', class_='caption sem')
                    
                    for p in detail_lines:
                        span_caption_sem = p.find('span', class_='caption sem')
                        if span_caption_sem:
                            inbound = span_caption_sem.find_parent('p')
                            if inbound:
                                offer.inbound_date = inbound.find('span', class_='date').get_text()
                                offer.inbound_departure_time = inbound.find('span', class_='from').find('strong').get_text()
                                offer.inbound_price = inbound.find('span', class_='subPrice').get_text()
                    
                    return offer
            else:
                print("Insufficient detail lines for offer")
        else:
            print("Text div not found for offer")
    except Exception as error:
        print("An expection occurred while parsing offer: ", error)
 
    return None   