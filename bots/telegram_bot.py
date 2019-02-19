import os
import logging
import requests
import json
from collections import deque
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transport.data_provider import DropBoxDataProvider

dbx_token = os.environ['DROPBOX_TOKEN']
telegram_token = os.environ['TELEGRAM_TOKEN']
port = int(os.environ['PORT'])
url_path = os.environ['URL_PATH']

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
dbx_provider = DropBoxDataProvider(dbx_token)

def start(bot, update):
    update.message.reply_text(
            "Hello! My name is Stella, and I will provide you with the actual information on prices of Ukrainian " \
            "gas stations.\n"
            "Simply type here a name of gas company you want to know about.\n"
            "Also, you can update my knowledge yourself by making and sending me photos of nearby gas stations` steles.\n"
            "To start, simply type 'start'. If you want to know more, type 'help'.")

def help(bot, update):
    update.message.reply_text("Need help? Still in development.")

def error(bot, update, error):
    logger.warning("Update {} caused error {}".format(update, error))

def send_file_dbx(bot, update):
    file_id = update.message.document.file_id

    new_file = requests.get("https://api.telegram.org/bot{}/getFile?file_id={}".format(telegram_token, file_id))
    loaded_data = json.loads(new_file.text)
    file_path = loaded_data["result"]["file_path"]

    down_path = "https://api.telegram.org/file/bot{}/{}".format(telegram_token, file_path)
    dirname, basename = os.path.split(file_path)
    dbx_path = "/telegram_files/" + basename
    dbx_provider.file_upload(down_path, dbx_path)

message_handlers = {Filters.document: send_file_dbx,}
command_handlers = {"start": start, "help": help,}

def main():
    updater = Updater(telegram_token)
    disp = updater.dispatcher
    disp.add_error_handler(error)
    deque(map(lambda kv: (disp.add_handler(CommandHandler(kv[0], kv[1]))), command_handlers.items()))
    deque(map(lambda kv: (disp.add_handler(MessageHandler(kv[0], kv[1]))), message_handlers.items()))
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=telegram_token)
    updater.bot.setWebhook(f'{url_path}/{telegram_token}')
    updater.idle()

if __name__ == '__main__':
    main()
