import telebot
from telebot import types

import db
from db import Handler

bot = telebot.TeleBot(token="")


@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    botton_1 = types.KeyboardButton("Купить запчасть")
    botton_2 = types.KeyboardButton("Записаться на ремонт")
    botton_3 = types.KeyboardButton("Задать вопрос")
    markup.add(botton_1)
    markup.add(botton_2)
    markup.add(botton_3)
    bot.send_message(message.chat.id,
                     'Нажмите: \n"Купить запчасть" для покупки запчастей\n"Записаться на ремонт"'
                     ' — для записи на ремонт\n "Задать вопрос" - для получения консультации ',
                     reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        h = db.Handler()
        h.safe_contact(message.contact)
    start(message)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == 'Купить запчасть':
        bot.send_message(message.chat.id, 'Введите парт номера через пробел')
        bot.register_next_step_handler(message, buy_parts)
    elif message.text == 'Записаться на ремонт':
        workshop_sing_up(message)
    elif message.text == "Задать вопрос":
        bot.send_message(message.chat.id, "Задайте ваш вопрос")
        bot.register_next_step_handler(message, user_question)


@bot.callback_query_handler(func=lambda call: True)
def sing_up_date(call):
    h = db.Handler()
    h.sing_up_repair(call.message.chat.id, call.data)


def buy_parts(message):
    h = Handler()
    x = h.create_order(message.text.split(), message.chat.id)
    bot.send_message(message.chat.id, f"Ваш заказ {x}")
    phone(message)


def phone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер",
                                        request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, 'Оставьте ваш номер телефона',
                     reply_markup=keyboard)


def workshop_sing_up(message):
    h = db.Handler()
    date_list = h.last_date()
    date_menu = telebot.types.InlineKeyboardMarkup()
    for item in date_list:
        date_menu.add(telebot.types.InlineKeyboardButton(text=str(item), callback_data=str(item)))
    bot.send_message(message.chat.id, text='Выбирете дату', reply_markup=date_menu)
    phone(message)


def user_question(message):
    h = db.Handler()
    h.safe_question(message.text, message.chat.id)
    phone(message)
    bot.send_message(message.chat.id, "Мы свяжемся с вами в ближайшее время, пожалуйста, оставьте ваш номер телефона")


bot.polling(none_stop=True, interval=0)
