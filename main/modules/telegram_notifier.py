# modules/telegram_notifier.py
import decimal

def send_notification(offers, bot, chat_id):
    for offer in offers:
        try:
            # Ensure prices are properly formatted and converted
            print(offer['Outbound Price (Azair)'])

            outbound_price = float(offer['Outbound Price (Azair)'].replace("€", "").strip())
            inbound_price = float(offer['Inbound Price (Azair)'].replace("€", "").strip())
            
            total_price = outbound_price + inbound_price
            offer['Total Price'] = total_price  # Updating the dictionary with the total price
            
            ryanair_outbound_price = offer.get('Ryanair Outbound Actual Price (if applicable)', 'N/A')
            ryanair_inbound_price = offer.get('Ryanair Inbound Actual Price (if applicable)', 'N/A')

            # Construct the notification message based on the requested structure
            message = (
                f"We found a great weekend escape deal!\n\n"
                f"Departure Date: {offer['Departure Date']}\n"
                f"Outbound Departure Time: {offer['Outbound Departure Time']}\n"
                f"Outbound Airline: {offer['Outbound Airline']}\n"
                f"Outbound Price (Azair): {offer['Outbound Price (Azair)']}\n"
                f"Ryanair Outbound Actual Price (if applicable): {ryanair_outbound_price}\n\n"
                
                f"Arrival Date: {offer['Arrival Date']}\n"
                f"Inbound Departure Time: {offer['Inbound Departure Time']}\n"
                f"Inbound Airline: {offer['Inbound Airline']}\n"
                f"Inbound Price (Azair): {offer['Inbound Price (Azair)']}\n"
                f"Ryanair Inbound Actual Price (if applicable): {ryanair_inbound_price}\n\n"

                f"Origin: {offer['Origin']} ({offer['Origin airport code']})\n"
                f"Destination: {offer['Destination']} ({offer['Destination airport code']})\n"
                f"---------------------------------------\n"
                f"Total Price: €{total_price:.2f}"
            )

            # Log the message for testing purposes
            print(message)

            # Send message to Telegram bot
            bot.send_message(chat_id, text=message)

        except (ValueError, KeyError) as e:
            print(f"Error calculating prices or sending message: {e}")

