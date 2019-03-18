import os
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
                     InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, \
                         CallbackQueryHandler
from stella_api.service_data import store_bot_data, upload_image_to_dbx
from bots.bot_services import get_station_by_location
import bots.constants as const
# TODO delete before production!:
from stella_api.image_recognition import digit_to_price

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PHOTO, CHOICE, SELECT_STATION, LOCATION, SET_DATA, GET_DATA, DATALOC, IN_DEV = range(8)


def start(bot, update):

    bot.send_message(chat_id=update.effective_message.chat_id,
                     text=const.start_text,
                     reply_markup=InlineKeyboardMarkup(const.start_keyboard))
    return CHOICE


def start_button(bot, update):
    query = update.callback_query
    if query.data == 'send':
        return send_location(bot, update)
    elif query.data == 'get':
        return getdata(bot, update)


def getdata(bot, update):
    query = update.callback_query
    location_button = KeyboardButton('Sent location', request_location=True)
    no_matter = KeyboardButton('Doesn\'t matter')
    bot.send_message(chat_id=query.message.chat_id,
                     text='Please share your location to get data depending your place '
                          'or press "Skip" if location doesn\'t matter',
                     reply_markup=ReplyKeyboardMarkup([[location_button], [no_matter]],
                                                      one_time_keyboard=True, resize_keyboard=True)
                     )
    return GET_DATA


def setdata(bot, update, location, user_data):
    stations = get_station_by_location(lat=location['latitude'], lng=location['longitude'])
    if not stations:
        bot.send_message(text="There are no gas stations in your location, please try again.",
                         chat_id=update.message.chat_id)
        return send_location(bot, update)
    user_data['stations'] = stations
    buttons = [[InlineKeyboardButton(text=st["name"]+f'\n{st["adress"]}',
                                     callback_data=stations.index(st))] for st in stations]
    bot.send_message(text="Please choose fuel company from the list: ",
                     chat_id=update.message.chat_id,
                     reply_markup=InlineKeyboardMarkup(buttons))
    return SELECT_STATION


def select_station(bot, update, user_data):
    query = update.callback_query
    user_data['gas_st'] = user_data['stations'][int(query.data)]
    bot.send_message(text='You\'ve selected "{}".\n Please send us your photo:'
                     .format(user_data['stations'][int(query.data)]['name']),
                     chat_id=query.message.chat_id)
    return PHOTO


def send_location(bot, update):
    location_button = KeyboardButton('Send current location', request_location=True)
    bot.send_message(chat_id=update.effective_message.chat_id,
                     text='Please, share you location so we can find nearest gas stations.\n'
                          'Tap the button if you are near gas station now, or choose location manually',
                     reply_markup=ReplyKeyboardMarkup([[location_button]],
                                                      one_time_keyboard=True, resize_keyboard=True))
    return LOCATION


def got_location(bot, update, user_data):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Thanks!", reply_markup=ReplyKeyboardRemove())
    loc = update.message.location
    return setdata(bot, update, loc, user_data)


def get_data_by_location(bot, update):

    bot.send_message(chat_id=update.message.chat_id, text="ok!",
                     reply_markup=ReplyKeyboardRemove())
    bot.send_message(chat_id=update.message.chat_id, text="Please choose:",
                     reply_markup=InlineKeyboardMarkup(const.data_by_loc_keyboard))
    return DATALOC


def dataloc(bot, update):
    bot.send_message(chat_id=update.effective_message.chat_id,
                     text="Select types of fuel:\n\nIN DEVELOPMENT",
                     reply_markup=ReplyKeyboardRemove())
    return start(bot, update)


def help(bot, update):
    update.message.reply_text("Still in development. /start")


def error(bot, update, error):
    logger.warning("Update {} caused error {}".format(update, error))


def cancel(bot, update):
    return ConversationHandler.END


def send_file_dbx(bot, update, user_data):
    # TODO move this to services, realize else
    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
    else:
        pass
    user_id = update.message.from_user.username
    station_name = user_data['gas_st']['name']
    adress = user_data['gas_st']['adress']
    lat, lng = user_data['gas_st']['lat'], user_data['gas_st']['lng']
    dbx_path = upload_image_to_dbx(file_id)
    bot.send_message(chat_id=update.message.chat_id, text="download success! "+dbx_path)
# TODO uncomment to solve trouble with alchemy:
    #response = store_bot_data(telegram_id=user_id, image_link=dbx_path, company_name=station_name,
    #                          address=adress, lat=lat, lng=lng)
    is_recognized, fuel_type, price = digit_to_price(dbx_path)
    if is_recognized:
        bot.send_message(chat_id=update.message.chat_id, text=f"Recognized!\n"
        f"A{fuel_type}: {price}грн")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Failed to recognize")
    return start(bot, update)


def main(poll=True):
    telegram_token = os.environ['TELEGRAM_TOKEN']
    updater = Updater(telegram_token)
    disp = updater.dispatcher
    disp.add_error_handler(error)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), ],

        states={
            CHOICE: [CallbackQueryHandler(start_button)],
            LOCATION: [MessageHandler(Filters.location, got_location, pass_user_data=True)],
            GET_DATA: [MessageHandler(Filters.location, get_data_by_location), MessageHandler(Filters.text, dataloc)],
            DATALOC: [CallbackQueryHandler(dataloc)],
            SELECT_STATION: [CallbackQueryHandler(select_station, pass_user_data=True)],
            PHOTO: [(MessageHandler(Filters.document, send_file_dbx, pass_user_data=True)),
                    MessageHandler(Filters.photo, send_file_dbx, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    disp.add_handler(conv_handler)
    disp.add_handler(CommandHandler("help", help))
    disp.add_handler(CommandHandler("start", start))
    disp.add_error_handler(error)

    if poll:
        updater.start_polling()
        updater.idle()
    else:
        updater.start_webhook(listen="0.0.0.0",
                              port=int(os.environ['PORT']),
                              url_path=telegram_token)
        updater.bot.setWebhook(f'{os.environ["URL_PATH"]}/{telegram_token}')
        updater.idle()


if __name__ == '__main__':
    main()
