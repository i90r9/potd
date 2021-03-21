import logging

import telebot

import db
import settings

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


def format_reply(msg):
    return f'*{msg.proverb}*\n"_{msg.meaning}_"'


def gen_markup():
    markup = telebot.types.ReplyKeyboardMarkup()
    btn = telebot.types.KeyboardButton("Get Me Another One!")
    markup.add(btn)
    return markup


if __name__ == "__main__":

    bot = telebot.TeleBot(settings.API_TOKEN)

    data_mgr = db.DataManager(db.DatabaseManager())

    @bot.message_handler(commands=["help", "start"])
    def send_welcome(message):
        logger.info(f"Got message from user: {message.from_user}")
        bot.reply_to(
            message,
            "Hi, this is ProverbOfTheDay Bot. "
            'Push "Get Me Another One!" button or send any message and I\'ll reply you with a proverb',
            reply_markup=gen_markup(),
        )

    @bot.message_handler(commands=["subscribe"])
    def subscribe(message):
        pass

    @bot.message_handler(commands=["unsubscribe"])
    def unsubscribe(message):
        pass
        
    @bot.message_handler(func=lambda message: True)
    def send_proverb(message):
        logger.info(f"Got message from user: {message.from_user}")
        bot.reply_to(
            message,
            format_reply(data_mgr.get_random()),
            parse_mode="markdown",
            reply_markup=gen_markup(),
        )

    bot.polling()
