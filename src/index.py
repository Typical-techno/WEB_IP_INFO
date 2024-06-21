# main.py
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from scripts.subDomains import get_unique_common_names
from scripts.internetDB import resolve_domain, internetdb_query
from scripts.centralops import centralops_query

# Function to split a long message into chunks
def split_message(message, chunk_size=4096):
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

# Define the start command handler with enhanced message
async def start(update: Update, context: CallbackContext) -> None:
    start_message = (
        "👋 Hello! Welcome to the Website Scanner Bot.\n\n"
        "🔍 Here you can scan any website and get its data, like subdomains, IP details, domain details, and more.\n\n"
        "To get started, use the following commands:\n"
        "➡️ `/sub <domain>` to get the subdomains of a website.\n"
        "➡️ `/shodan <domain>` to get Shodan InternetDB details for a domain.\n\n"
        "For example: `/sub example.com` or `/shodan example.com`\n\n"
        "Happy scanning! 🕵️‍♂️"
    )
    await update.message.reply_text(start_message)

# Define the handler to fetch and send the common names based on user input
async def get_common_names(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('⚠️ Please provide a domain. Usage: /sub <domain>')
        return

    domain = context.args[0]
    unique_common_names = get_unique_common_names(domain)
    
    if unique_common_names:
        formatted_names = "\n\n".join(unique_common_names)
        message = f"🌐 Common Names for {domain}:\n\n{formatted_names}"
    else:
        message = f"❌ No common names found for {domain}."
    
    # Split the message if it's too long
    message_chunks = split_message(message)
    
    for chunk in message_chunks:
        await update.message.reply_text(chunk)

# Define the handler to fetch and send the Shodan InternetDB data based on user input
async def get_shodan_data(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('⚠️ Please provide a domain. Usage: /shodan <domain>')
        return

    domain = context.args[0]
    ip_addresses = resolve_domain(domain)
    
    if not ip_addresses:
        await update.message.reply_text(f"❌ Unable to resolve IP addresses for {domain}.")
        return
    
    result_txt = internetdb_query(ip_addresses)
    
    # Split the message if it's too long
    message_chunks = split_message(result_txt)
    
    for chunk in message_chunks:
        await update.message.reply_text(chunk)

# Define the handler to fetch and send the CentralOps data based on user input
async def get_centralops_data(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('⚠️ Please provide a domain. Usage: /ip <domain>')
        return

    domain = context.args[0]
    
    # Query CentralOps
    txt_report, addresses_list = centralops_query(domain, requests.get)

    # Prepare response
    if addresses_list:
        addresses_text = "\n\n".join(addresses_list)
        message = f"ℹ️ Domain Information for {domain}:\n\n{txt_report}\n\nAddresses:\n{addresses_text}"
    else:
        message = f"❌ No information found for {domain}."

    # Split the message if it's too long
    message_chunks = split_message(message)
    
    for chunk in message_chunks:
        await update.message.reply_text(chunk)

def main():
    # Your bot token from BotFather
    BOT_TOKEN = '6665952955:AAHsv-6y0i9kb3e3fhT-0gFLv2RXTnaOvv8'
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the /start, /sub, and /shodan commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sub", get_common_names))
    application.add_handler(CommandHandler("ipports", get_shodan_data))
    application.add_handler(CommandHandler("ip", get_centralops_data))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
