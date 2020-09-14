"""Если понадобиться включить прокси, то необходимо добавить после 11 строки следующий код:

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}"""

import logging
import re

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem

from mybot import settings

logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S'
                    )


def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь! Ты вызвал команду /start')


def wordcount(update, context):
    user_text = str(update.message.text[10:])
    print(user_text)
    if len(user_text) == 0:
        update.message.reply_text('Что мне считать, если ты мне отправил пустоту?')
    else:
        update.message.reply_text(f"Количество слов: {len(re.findall('[a-zA-Zа-яА-Я_]+', user_text))}")


def coord(update, context):
    planets = {'mercury': ephem.Mercury,
               'venus': ephem.Venus,
               'mars': ephem.Mars,
               'jupiter': ephem.Jupiter,
               'saturn': ephem.Saturn,
               'uranus': ephem.Uranus,
               'neptune': ephem.Neptune}
    date = ephem._datetime.utcnow()
    user_text = str(update.message.text.split()[-1]).lower()
    if user_text in planets.keys():
        update.message.reply_text(f'Планета {user_text.capitalize()} '
                                  f'находится в созвездии {ephem.constellation(planets[user_text](date))[-1]}')
    else:
        update.message.reply_text('Запрос неверен. Нужно запрашивать планету на англ. языке.')


def full_moon(update, context):
    date = ephem._datetime.utcnow()
    update.message.reply_text(f"Следующее полнолуние будет {ephem.next_full_moon(date)}")


def talk_to_me(update, context):
    user_text = str(update.message.text)
    print(user_text)
    logging.info(user_text)
    update.message.reply_text(user_text)


def main():
    # Создаем бота и передаем ему ключ для авторизации на серверах Telegram
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("wordcount", wordcount))
    dp.add_handler(CommandHandler("fullmoon", full_moon))
    dp.add_handler(CommandHandler("planet", coord))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал!')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()


if __name__ == '__main__':
    main()
