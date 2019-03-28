from telegram import InlineKeyboardButton


start_keyboard = [[InlineKeyboardButton("Get prices", callback_data='get'),
                   InlineKeyboardButton("Send photo", callback_data='send')]]

start_text = "Hello! My name is Stella, and I will provide you with the actual information " \
             "on prices of Ukrainian gas stations.\nSimply tap the button, what do you want\n" \
             "If something goes wrong, simply type:\n " \
             "'/cancel' then '/start'. If you need help, type '/help'."

data_by_loc_keyboard = [
                [InlineKeyboardButton("Last updated prices at closest stations", callback_data='dev')],
                [InlineKeyboardButton("Yesterday prices at closest stations", callback_data='dev')],
                [InlineKeyboardButton("Prices at nearest station by week", callback_data='dev')],
                [InlineKeyboardButton("Prices at nearest station by month", callback_data='dev')],
                [InlineKeyboardButton("Prices by specific data", callback_data='dev')],
                [InlineKeyboardButton("Prices by data range", callback_data='dev')]
                ]

getdata_keyboard = [
                [InlineKeyboardButton(text='Change Filters', callback_data='filters')],
                [InlineKeyboardButton(text='OK', callback_data='ok')]
                #[InlineKeyboardButton(text='date range', callback_data='more')],
                #[InlineKeyboardButton(text='location', callback_data='more')],
                #[InlineKeyboardButton(text='Companies', callback_data='more')],
                #[InlineKeyboardButton(text='Gas stations', callback_data='more')],
                #[InlineKeyboardButton(text='Fuel type', callback_data='more')],
                #[InlineKeyboardButton(text='max/min or average', callback_data='more')]
                ]

getdata_text = 'Data filters:\nLocation - No matter\nDate range - Last 10 days\n' \
               'Companies - all\nGas stations - all\nFuel type - all\nStatistic - none'
