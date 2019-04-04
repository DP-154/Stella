import logging
import os

from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler, RegexHandler

import bots.calendar.telegramcalendar as telegramcalendar
import bots.constants as const
from bots.bot_services import get_gas_staton_info_from_google, pagination_output
from database.db_connection import session_maker
from database.db_query_bot import query_all_price_period
from database.queries import list_fuel_company_names, list_fuels, custom_query
from services.service_data import store_bot_data, upload_image_to_dbx, get_telegram_upload_image_paths
from stella_api.helpers import query_to_list


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PHOTO, CHOICE, SELECT_STATION, LOCATION, SET_DATA, GET_DATA, FILTERS, IN_DEV, PAGINATION,\
    STEPCHANGE, FILTERS_CHANGE, DATE_CHOICE, DATE_OR_RANGE, DATE_RANGE_CHOICE, \
    FILTER_SELECTION, STAT_FUNCTION = range(16)


def start(bot, update, user_data):
    if not user_data.get('start_msg_id'):
        msg = bot.send_message(chat_id=update.effective_message.chat_id,
                               text=const.start_text,
                               reply_markup=InlineKeyboardMarkup(const.start_keyboard))
        user_data['start_msg_id'] = msg['message_id']
    else:
        safe = user_data['start_msg_id']
        user_data.clear()
        user_data['start_msg_id'] = safe
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
    keyboard = [
                [InlineKeyboardButton(text='Change Filters', callback_data='filters')],
                [InlineKeyboardButton(text='Reset', callback_data='reset')],
                [InlineKeyboardButton(text='OK', callback_data='ok')]
                ]
    if not user_data.get('date_from') and not user_data.get('date_to'):
        if user_data.get("date"):
            date_text = user_data['date'].strftime("%d.%m.%Y")
        else:
            date_text = "Last 10 days"

    else:
        date_text = f"from {user_data.get('date_from').strftime('%d.%m.%Y')} " \
                    f"to {user_data.get('date_to').strftime('%d.%m.%Y')}"
    bot.edit_message_text(chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          text=f'Date: {date_text}\n\n'                               
                               f'Companies: {", ".join(user_data.get("selected_companies", ["all"]))}\n\n'
                               f'Fuel type: {", ".join(user_data.get("selected_fuels", ["all"]))}\n\n'
                               f'Statistic: {user_data.get("stat_func", "None")}',
                          reply_markup=InlineKeyboardMarkup(keyboard))
    return FILTERS


def filters(bot, update, user_data):
    query = update.callback_query
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    if query.data == 'ok':
        return data_from_db(bot, update, user_data)
    elif query.data == 'filters':
        return choose_filters(bot, update, user_data)
    elif query.data == 'reset':
        safe = user_data['start_msg_id']
        user_data.clear()
        user_data['start_msg_id'] = safe
        return getdata(bot, update, user_data)


def choose_filters(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    keyboard = [[InlineKeyboardButton(text='Date', callback_data='date')],
                [InlineKeyboardButton(text='Fuel companies', callback_data='selected_companies')],
                [InlineKeyboardButton(text='Fuel types', callback_data='selected_fuels')],
                [InlineKeyboardButton(text='Statistic', callback_data='stat_func')]]
    bot.edit_message_text(chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          text='Choose to change:',
                          reply_markup=InlineKeyboardMarkup(keyboard))
    return FILTERS_CHANGE


def filters_change(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    query = update.callback_query

    if query.data == 'date':
        keyboard = [[InlineKeyboardButton(text='Specific Date', callback_data='spec_date')],
                    [InlineKeyboardButton(text='Date range', callback_data='date_range')]]
        bot.edit_message_text(chat_id=update.effective_message.chat_id,
                              message_id=user_data['start_msg_id'],
                              text="One day or range?",
                              reply_markup=InlineKeyboardMarkup(keyboard))
        return DATE_OR_RANGE
    elif query.data == 'selected_companies':
        session = session_maker()
        response = list_fuel_company_names(session)
        session.close()
        response = list(set(response))
        user_data['response'] = response
        return selector(bot, update, user_data, response, query.data)
    elif query.data == 'selected_fuels':
        session = session_maker()
        response = list_fuels(session)
        session.close()
        response = list(set(response))
        user_data['response'] = response
        return selector(bot, update, user_data, response, query.data)
    elif query.data == 'stat_func':
        keyboard = [[InlineKeyboardButton(text='Max', callback_data='max')],
                    [InlineKeyboardButton(text='Average', callback_data='avg')],
                    [InlineKeyboardButton(text='Min', callback_data='min')],
                    ]
        bot.edit_message_text(chat_id=update.effective_message.chat_id,
                              message_id=user_data['start_msg_id'],
                              text="Choose statistic function:",
                              reply_markup=InlineKeyboardMarkup(keyboard))
        return STAT_FUNCTION


def stat_function(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    query = update.callback_query
    user_data['stat_func'] = query.data
    return getdata(bot, update, user_data)


def selector(bot, update, user_data, response, key):
    keyboard = []
    limit_per_string = 0
    if key == 'selected_companies':
        limit_per_string = 0
    elif key == 'selected_fuels':
        limit_per_string = 2
    user_data['key'] = key
    counter = 0
    keystring = []
    for i in response:
        if i not in user_data.get(key, []):
            keystring.append(InlineKeyboardButton(text=i, callback_data=i))
            if counter >= limit_per_string:
                keyboard.append(keystring)
                keystring = []
                counter = 0
            else:
                counter += 1
    keyboard.append(keystring)
    keyboard.append([InlineKeyboardButton(text='- = RESET = -', callback_data='reset')])
    keyboard.append([InlineKeyboardButton(text='- = OK = -', callback_data='Ok')])
    bot.edit_message_text(chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          text=f'Please, select fuel company from list, then press "OK".\n'
                               f'You\'ve selected: '
                               f'{", ".join(user_data.get(key, ""))}',
                          reply_markup=InlineKeyboardMarkup(keyboard))
    return FILTER_SELECTION


def filter_selection(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    key = user_data['key']
    if update.callback_query.data == "Ok":
        return getdata(bot, update, user_data)
    if update.callback_query.data == "reset":
        user_data['response'].extend(user_data[key])
        user_data[key] = []
        return selector(bot, update, user_data, user_data['response'], key)
    if not user_data.get(key):
        user_data[key] = []
    user_data[key].append(update.callback_query.data)
    user_data['response'].remove(update.callback_query.data)
    return selector(bot, update, user_data, user_data['response'], key)


def date_range_or_spec(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    query = update.callback_query
    if query.data == 'spec_date':
        bot.edit_message_text(chat_id=update.effective_message.chat_id,
                              message_id=user_data['start_msg_id'],
                              text="Please select a date: ",
                              reply_markup=telegramcalendar.create_calendar())
        return DATE_CHOICE
    elif query.data == 'date_range':
        user_data['date_from'], user_data['date_to'] = None, None
        bot.edit_message_text(chat_id=update.effective_message.chat_id,
                              message_id=user_data['start_msg_id'],
                              text="Please select date from: ",
                              reply_markup=telegramcalendar.create_calendar())
        return DATE_RANGE_CHOICE


def date_range_choice(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    if not user_data.get('date_from'):
        selected, date_from = telegramcalendar.process_calendar_selection(bot, update)
        if selected:
            user_data['date_from'] = date_from
            bot.edit_message_text(chat_id=update.effective_message.chat_id,
                                  message_id=user_data['start_msg_id'],
                                  text="Please select date to: ",
                                  reply_markup=telegramcalendar.create_calendar())
            return DATE_RANGE_CHOICE
    if not user_data.get('date_to'):
        selected, date_to = telegramcalendar.process_calendar_selection(bot, update)
        if selected:
            user_data['date_to'] = date_to
            if user_data['date_from'] > user_data['date_to']:
                bot.edit_message_text(chat_id=update.effective_message.chat_id,
                                      message_id=user_data['start_msg_id'],
                                      text="Incorrect input!\n\nPlease repeat.\n"
                                           "Please select date from: ",
                                      reply_markup=telegramcalendar.create_calendar())
                user_data['date_from'], user_data['date_to'] = None, None
                return DATE_RANGE_CHOICE
            return getdata(bot, update, user_data)


def date_choice(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    selected, date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        if user_data.get('date_from'):
            user_data['date_from'] = None
        if user_data.get('date_to'):
            user_data['date_to'] = None
        user_data['date'] = date
        return getdata(bot, update, user_data)


def setdata(bot, update, location, user_data, more=None):
    if not user_data.get('radius'):
        user_data['radius'] = 50
    if more:
        user_data['radius'] += 600
        bot.answer_callback_query(text=f'radius={user_data.get("radius", "min")}m',
                                  callback_query_id=update.callback_query.id)
        stations = get_gas_staton_info_from_google(
                                    lat=location['latitude'],
                                    lng=location['longitude'],
                                    radius=user_data['radius']
                                    )
    else:
        stations = get_gas_staton_info_from_google(lat=location['latitude'], lng=location['longitude'])
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


def data_from_db(bot, update, user_data):
    bot.answer_callback_query(callback_query_id=update.callback_query.id)
    bot.edit_message_text(chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          text="processing...")
    session = session_maker()
    response = query_all_price_period(session)
    session.close()
    user_data['db_output'] = query_to_list(response)
    user_data['gas_per_msg'] = 2
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
        safe = user_data['start_msg_id']
        user_data.clear()
        user_data['start_msg_id'] = safe
        return start(bot, update, user_data)


def step_change(bot, update, user_data):
    bot.edit_message_text(text="Choose number of gas stations per page, or type it from keyboard:",
                          chat_id=update.effective_message.chat_id,
                          message_id=user_data['start_msg_id'],
                          reply_markup=InlineKeyboardMarkup(const.step_change_keyboard))
    return STEPCHANGE


def step_set(bot, update, user_data):
    query = update.callback_query
    if update.callback_query:
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
            GET_DATA: [CallbackQueryHandler(data_from_db, pass_user_data=True)],
            FILTERS: [CallbackQueryHandler(filters, pass_user_data=True)],
            SELECT_STATION: [CallbackQueryHandler(select_station, pass_user_data=True)],
            PHOTO: [(MessageHandler(Filters.document, send_file_dbx, pass_user_data=True)),
                    MessageHandler(Filters.photo, send_file_dbx, pass_user_data=True)],
            PAGINATION: [CallbackQueryHandler(pagin_handler, pass_user_data=True)],
            STEPCHANGE: [CallbackQueryHandler(step_set, pass_user_data=True),
                         RegexHandler(r'\d{1,3}', step_set, pass_user_data=True)],
            FILTERS_CHANGE: [CallbackQueryHandler(filters_change, pass_user_data=True)],
            DATE_CHOICE: [CallbackQueryHandler(date_choice, pass_user_data=True)],
            DATE_OR_RANGE: [CallbackQueryHandler(date_range_or_spec, pass_user_data=True)],
            DATE_RANGE_CHOICE: [CallbackQueryHandler(date_range_choice, pass_user_data=True)],
            FILTER_SELECTION: [CallbackQueryHandler(filter_selection,
                                                            pass_user_data=True)],
            STAT_FUNCTION: [CallbackQueryHandler(stat_function, pass_user_data=True)]
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





