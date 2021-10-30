from bot import BUTTONS
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


async def main(language) -> ReplyKeyboardMarkup:
    button_1 = KeyboardButton(BUTTONS[language]["main"]["1"])

    keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(button_1)
    return keyboard_markup


async def return_button(language) -> ReplyKeyboardMarkup:
    button_1 = KeyboardButton(BUTTONS[language]["main"]["3"])

    keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(button_1)
    return keyboard_markup


async def my_cards_reply_markup(language) -> ReplyKeyboardMarkup:
    button_1 = KeyboardButton(BUTTONS[language]["my_cards"]["1"])
    button_2 = KeyboardButton(BUTTONS[language]["main"]["3"])

    keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(button_1)
    keyboard_markup.row(button_2)
    return keyboard_markup


async def my_cards_inline_markup(language, user) -> InlineKeyboardMarkup:
    buttons = []
    for key in user.cards.keys():
        buttons.append(InlineKeyboardButton(key, callback_data=f'show_{key}'))
    keyboard_markup = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard_markup.add(*buttons)
    return keyboard_markup


async def delete_card(language, shop_name) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(BUTTONS[language]['my_cards']['2'], callback_data=f'delete_{shop_name}')
    keyboard_markup = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row(button_1)
    return keyboard_markup


async def shop_list(language, shops) -> ReplyKeyboardMarkup:
    buttons = []
    for shop in shops:
        if language == 'ru':
            buttons.append(KeyboardButton(shop.ru_name))
        elif language == 'en':
            buttons.append(KeyboardButton(shop.en_name))

    keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    keyboard_markup.add(*buttons)
    button_2 = KeyboardButton(BUTTONS[language]['my_cards']['3'])
    button_1 = KeyboardButton(BUTTONS[language]["main"]["3"])
    keyboard_markup.row(button_2)
    keyboard_markup.row(button_1)
    return keyboard_markup
