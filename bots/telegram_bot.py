import os
import sys
import logging
import requests
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transport.data_provider import DropBoxDataProvider

dbx_token = os.environ.get('DROPBOX_TOKEN')
telegram_token = os.environ.get('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
dbx_provider = DropBoxDataProvider(dbx_token)

def start(bot, update):
    update.message.reply_text(
            "Hello! My name is Stella, and I will provide you with the actual information on prices of Ukrainian" \
            "gas stations.\n"
            "Simply type here a name of gas company you want to know about.\n"
            "Also, you can update my knowledge yourself by making and sending me photos of nearby gas stations` steles.\n"
            "To start, simply type 'start'. If you want to know more, type 'help'.")

def help(bot, update):
    update.message.reply_text("Need help? Still in development.")

def echo(bot, update):
    update.message.reply_text(update.message.text)

def error(bot, update, error):
    logger.warning("Update {} caused error {}".format(update, error))

def send_file_dbx(bot, update):
    file_id = update.message.document.file_id

    new_file = requests.get("https://api.telegram.org/bot{}/getFile?file_id={}".format(telegram_token, file_id))
    loaded_data = json.loads(new_file.text)
    file_path = loaded_data["result"]["file_path"]

    down_file = requests.get("https://api.telegram.org/file/bot{}/{}".format(telegram_token, file_path))
    dirname, basename = os.path.split(file_path)
    root_dir = os.path.splitdrive(sys.executable)[0]
    new_path = os.path.join(root_dir + os.sep, "telegram_bot", dirname, basename)
    dbx_path = "/telegram_files/" + basename

    if not os.path.exists(os.path.dirname(new_path)):
        os.makedirs(os.path.dirname(new_path))

    with open(new_path, 'wb') as output:
        output.write(down_file.content)
    dbx_provider.file_upload(new_path, dbx_path)

def main():
    updater = Updater(telegram_token)
    disp = updater.dispatcher

    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", help))
    disp.add_handler(MessageHandler(Filters.document, send_file_dbx))
    disp.add_handler(MessageHandler(Filters.photo, send_file_dbx))
    disp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

    print(disp.handlers())


if __name__ == '__main__':
    main()

