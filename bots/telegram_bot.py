import os
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
                     InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, \
                         CallbackQueryHandler, RegexHandler
from services.service_data import store_bot_data, upload_image_to_dbx, get_telegram_upload_image_paths
from bots.bot_services import gas_station_info, pagination_output
import bots.constants as const
from database.db_query_bot import query_all_price_period
from database.queries import session_scope
from stella_api.helpers import query_to_list

# TODO db queries
# TODO calendar
# TODO database connection exeption, empty base exeption, alert user about these


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PHOTO, CHOICE, SELECT_STATION, LOCATION, SET_DATA, GET_DATA, DATALOC, IN_DEV, PAGINATION,\
    STEPCHANGE = range(10)


def start(bot, update, user_data):
    if not user_data.get('start_msg_id'):
        msg = bot.send_message(chat_id=update.effective_message.chat_id,
                               text=const.start_text,
                               reply_markup=InlineKeyboardMarkup(const.start_keyboard))
        user_data['start_msg_id'] = msg['message_id']
    else:
        bot.edit_message_text(chat_id=update.effective_message.chat_id,
                              text=const.start_text,
                              message_id=user_data['start_msg_id'],
                              reply_markup=InlineKeyboardMarkup(const.start_keyboard))
    return CHOICE


def start_button(bot, update, user_data):
    query = update.callback_query
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    if query.data == 'send':
        return send_location(bot, update)
    elif query.data == 'get':
        return getdata(bot, update, user_data)


def getdata(bot, update, user_data):
    keyboard = const.getdata_keyboard
    bot.edit_message_text(chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          text=const.getdata_text,
                          reply_markup=InlineKeyboardMarkup(keyboard))
    return GET_DATA


def setdata(bot, update, location, user_data, more=None):
    if not user_data.get('radius'):
        user_data['radius'] = 50
    if more:
        user_data['radius'] += 600
        bot.answer_callback_query(text=f'radius={user_data.get("radius", "min")}m',
                                  callback_query_id=update.callback_query.id)
        stations = gas_station_info(
                                    lat=location['latitude'],
                                    lng=location['longitude'],
                                    radius=user_data['radius']
                                    )
    else:
        stations = gas_station_info(lat=location['latitude'], lng=location['longitude'])
    if not stations:
        bot.send_message(text="There are no gas stations in your location, please try again.",
                         chat_id=update.message.chat_id)
        return send_location(bot, update)
    user_data['stations'] = stations
    user_data['usr_location'] = location
    more_button = [InlineKeyboardButton(text='more...',
                   callback_data='more')]
    buttons = [[InlineKeyboardButton(text=st["name"]+f'\n{st["address"]}',
                                     callback_data=stations.index(st))] for st in stations]
    buttons.append(more_button)
    msg = bot.send_message(text="Please choose gas station from the list or tap 'more': ",
                           chat_id=update.effective_message.chat_id,
                           reply_markup=InlineKeyboardMarkup(buttons))
    user_data['stations_msg_id'] = msg['message_id']
    return SELECT_STATION

# TODO confirmation selected station by sending its location to user


def select_station(bot, update, user_data):
    query = update.callback_query
    if query.data == 'more':
        return more_stations(bot, update, user_data)
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    user_data['gas_st'] = user_data['stations'][int(query.data)]
    bot.send_message(text='You\'ve selected "{}".\n Please send us your photo:'
                     .format(user_data['stations'][int(query.data)]['name']),
                     chat_id=query.message.chat_id)
    user_data.pop("radius", None)
    return PHOTO


def more_stations(bot, update, user_data):
    bot.delete_message(chat_id=update.effective_message.chat_id,
                       message_id=user_data['stations_msg_id'])
    return setdata(bot, update, user_data['usr_location'], user_data, more=True)


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
    bot.send_message(chat_id=chat_id, text="Ok! Searching gas stations...",
                     reply_markup=ReplyKeyboardRemove())
    loc = update.message.location
    return setdata(bot, update, loc, user_data)


def dataloc(bot, update, user_data):
    bot.answer_callback_query(text='Filters in development...',
                              callback_query_id=update.callback_query.id)
    bot.edit_message_text(chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          text="processing...")
    with session_scope() as session:
        response = query_all_price_period(session)
    user_data['db_output'] = query_to_list(response)
    user_data['gas_per_msg'] = 5
    user_data['position'] = 0
    return pagination(bot, update, user_data)


def pagination(bot, update, user_data):
    keyboard = [InlineKeyboardButton('Prev', callback_data='prev'),
                InlineKeyboardButton(f"{user_data['gas_per_msg']} per msg", callback_data='step'),
                InlineKeyboardButton('Next', callback_data='next')]
    exit_button = [InlineKeyboardButton('EXIT', callback_data='exit')]
    if (user_data['position'] + user_data['gas_per_msg']) >= (len(user_data['db_output'])):
        keyboard[2] = InlineKeyboardButton('  ', callback_data='sleep')
    if user_data['position'] == 0:
        keyboard[0] = InlineKeyboardButton('  ', callback_data='sleep')
    output, user_data['position'] = pagination_output(user_data['db_output'],
                                                      user_data['position'],
                                                      user_data['gas_per_msg'])
    bot.edit_message_text(text=output,
                          chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          reply_markup=InlineKeyboardMarkup([keyboard, exit_button]))
    return PAGINATION


def pagin_handler(bot, update, user_data):
    query = update.callback_query
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    if query.data == 'prev':
        user_data['position'] = (user_data['position'] - 2*user_data['gas_per_msg'])
        return pagination(bot, update, user_data)
    elif query.data == 'step':
        return step_change(bot, update, user_data)
    elif query.data == 'next':
        return pagination(bot, update, user_data)
    elif query.data == 'exit':
        return start(bot, update, user_data)


def step_change(bot, update, user_data):
    keyboard = [[InlineKeyboardButton('1', callback_data=1),
                InlineKeyboardButton('2', callback_data=2),
                InlineKeyboardButton('3', callback_data=3)],
                [InlineKeyboardButton('4', callback_data=4),
                InlineKeyboardButton('5', callback_data=5),
                InlineKeyboardButton('6', callback_data=6)],
                [InlineKeyboardButton('7', callback_data=7),
                InlineKeyboardButton('8', callback_data=8),
                InlineKeyboardButton('9', callback_data=9)]]
    bot.edit_message_text(text="Choose number of gas stations per page, or type it from keyboard:",
                          chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          reply_markup=InlineKeyboardMarkup(keyboard))
    return STEPCHANGE


def step_set(bot, update, user_data):
    query = update.callback_query
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    if query:
        user_data['gas_per_msg'] = int(query.data)
    else:
        user_data['gas_per_msg'] = int(update.message.text)
    user_data['position'] = 0
    return pagination(bot, update, user_data)


def helpme(bot, update):
    update.message.reply_text("Still in development. /start")


def error(bot, update, err):
    logger.warning("Update {} caused error {}".format(update, err))


def cancel(bot, update, user_data):
    user_data.clear()
    return ConversationHandler.END


def send_file_dbx(bot, update, user_data):
    # TODO move this to services, realize else
    if update.message.document:
        file_id = update.message.document.file_id
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
    else:
        file_id = None
        pass
    user_id = update.message.from_user.id
    station_name = user_data['gas_st']['name']
    address = user_data['gas_st']['address']
    lat, lng = user_data['gas_st']['lat'], user_data['gas_st']['lng']
    tg_down_path, dbx_path = get_telegram_upload_image_paths(file_id)

    dbx_path, dbx_link = upload_image_to_dbx(tg_down_path, dbx_path)

    msg = bot.send_message(chat_id=update.message.chat_id, text="download success!\nRecognition...")

    response = store_bot_data(telegram_id=user_id, image_link=tg_down_path, image_path=dbx_path,
                              company_name=station_name, address=address)
    bot.edit_message_text(chat_id=update.message.chat_id, message_id=msg['message_id'], text=response)
    user_data.clear()
    return start(bot, update, user_data)


def main(poll=True):
    telegram_token = os.environ['TELEGRAM_TOKEN']
    updater = Updater(telegram_token)
    disp = updater.dispatcher
    disp.add_error_handler(error)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True), ],

        states={
            CHOICE: [CallbackQueryHandler(start_button, pass_user_data=True)],
            LOCATION: [MessageHandler(Filters.location, got_location, pass_user_data=True)],
            GET_DATA: [CallbackQueryHandler(dataloc, pass_user_data=True)],
            DATALOC: [CallbackQueryHandler(dataloc, pass_user_data=True)],
            SELECT_STATION: [CallbackQueryHandler(select_station, pass_user_data=True)],
            PHOTO: [(MessageHandler(Filters.document, send_file_dbx, pass_user_data=True)),
                    MessageHandler(Filters.photo, send_file_dbx, pass_user_data=True)],
            PAGINATION: [CallbackQueryHandler(pagin_handler, pass_user_data=True)],
            STEPCHANGE: [CallbackQueryHandler(step_set, pass_user_data=True),
                         RegexHandler('\d{1,3}', step_set, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
    )
    disp.add_handler(conv_handler)
    disp.add_handler(CommandHandler("help", helpme))
    disp.add_handler(CommandHandler("start", start, pass_user_data=True))
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





