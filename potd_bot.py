import logging

import telebot

import db
import service
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


class Balckboard:
    def __init__(self):
        self._blackboard = {}

    def add(self, key, value):
        self._blackboard[key] = value

    def remove(self, key):
        del self._blackboard[key]

    def get(self, key, default=None):
        return self._blackboard.get(key, default)


if __name__ == "__main__":

    bot = telebot.TeleBot(settings.API_TOKEN)

    data_mgr = db.DataManager(db.DatabaseManager())
    manager = service.SubscriptionManager()

    blackboard = Balckboard()

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
        logger.info(f"User subscribed")
        blackboard.add("chat_id", message.chat.id)
        manager.subscribe(callback=send_random)
        bot.reply_to(
            message,
            "You've been successfully subscribed to getting new proverbs each 10 secs."
            "Should you stop receiving proverbs please /unsubscribe",
        )

    @bot.message_handler(commands=["unsubscribe"])
    def unsubscribe(message):
        manager.unsubscribe()
        bot.reply_to(
            message,
            "You've been successfully unsubscribed.",
        )

    @bot.message_handler(func=lambda message: True)
    def send_proverb(message):
        logger.info(f"Got message from user: {message.from_user}")

        bot.reply_to(
            message,
            format_reply(data_mgr.get_random()),
            parse_mode="markdown",
            reply_markup=gen_markup(),
        )

    def send_random():
        bot.send_message(
            blackboard.get("chat_id"),
            format_reply(data_mgr.get_random()),
            parse_mode="markdown",
            reply_markup=gen_markup(),
        )

    try:
        manager.start()
        bot.polling()

    finally:
        manager.stop()
