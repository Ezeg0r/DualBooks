from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

languages = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='English')],
    [KeyboardButton(text='Russian')],
    [KeyboardButton(text='Polish')],
    [KeyboardButton(text='Belarusian')],

])

remove_keyboard = ReplyKeyboardRemove()