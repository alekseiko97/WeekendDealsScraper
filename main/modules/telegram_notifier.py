# modules/telegram_notifier.py

def send_notification(offer, bot, chat_id):
    # Construct notification message
    
    # TODO: fix calculation below, currently two strings are being concatenated
    total_price = offer.outbound_price + offer.inbound_price
    
    message = (
    f"We found a great weekend escape deal!\n\n"
    f"Departure: {offer.origin_airport} ({offer.outbound_departure_time})\n"
    f"Destination: {offer.destination_airport} ({offer.inbound_departure_time})\n"
    f"Outbound date: {offer.outbound_date}\n"
    f"Outbound price: {offer.outbound_price}\n"
    f"Inbound date: {offer.inbound_date}\n"
    f"Inbound price: {offer.inbound_price}\n"
    f"---------------------------------------\n"
    f"Total price: {total_price}"
    )
    
    print(message)

    # Send message to Telegram bot
    bot.send_message(chat_id, text=message)