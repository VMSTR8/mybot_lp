"""Если понадобиться включить прокси, то необходимо добавить после 11 строки следующий код:

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

    Игра в города сделана совместно с https://github.com/eyescreamxd"""

import logging
import re
import random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import ephem

from mybot import settings
from mybot.cities import cities_list

logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S'
                    )

user_data = {}  # {'username': ['city1', 'city2']} ключ — %username%; значение — список использованных названий
# городов в рамках раунда с конкретным пользователем


def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь! Ты вызвал команду /start')


def city_game(update, context):

    user = update.message.from_user.username  # выхватываем %username% из сообщения
    city = update.message.text[8:].lower()  # выхватываем всё, кроме комманды
    last_letter = city[-1]  # объявляем последнюю букву из названия города, на которую мы будем отвечать

    if city not in cities_list:  # проверка, если названия города пользователя нет в списке городов
        update.message.reply_text('Не знаю такого города. Давай другой.')
    else:
        if last_letter in 'ыъйь':  # если название города заканчивается на одну из указанных букв, то берём предпоследнюю
            last_letter = city[-2]

        if user not in user_data or len(user_data[user]) == 0:  # если пользователя нет в словаре
            user_data[user] = []   # инициализация пустого списка для ключа %username%
            user_data[user].append(city)  # добавляем в список название города, которое прислал юзер
            bot_city = random.choice([i for i in cities_list if i.startswith(last_letter) and i not in user_data[user]])  # составляем список названий городов, которые начинаются на нужную букву и не были использованы. Выбираем рандомное название города
            update.message.reply_text(bot_city)  # отвечаем рандомным названием
            user_data[user].append(bot_city)  # добавляем рандомное название в список использованных для этого юзера
        else:
            if len(cities_list) == len(user_data[user]):  # если длина списка использованных названий городов равна длине известных городов, то прекращаем игру
                update.message.reply_text('Известные мне города закончились. Обнуляем список городов.')
                user_data[user] = []  # обнуляем список использованных названий городов
            elif len([i for i in cities_list if i.startswith(last_letter) and i not in user_data[user]]) == 1:  # если закончился список известных городов на определённую букву, то также прекращаем игру
                random.choice([i for i in cities_list if i.startswith(last_letter) and i not in user_data[user]])  # отсылаем последнее название города
                update.message.reply_text('Использовано последнее слово на эту букву, которое я знаю. Начинаем сначала')
                user_data[user] = []  # обнуляем список
            else:
                start_letter = user_data[user][-1][-1]  # объявляем букву, на которую должен ответить пользователь
                if start_letter in 'ыъйь':  # если название города заканчивается на одну из указанных букв, то берём предпоследнюю
                    start_letter = user_data[user][-1][-2]

                if start_letter != city[0]:  # если название города пользователя начинается не с той буквы, ругаем его
                    update.message.reply_text('Схитрить решил? Отвечай честно!')
                else:
                    if city in user_data[user]:  # если название города уже было использовано, ругаем пользователя
                        update.message.reply_text('Схитрить решил? Отвечай честно!')
                    else:
                        user_data[user].append(city)  # добавляем название города в список использованных в этой сессии юзера
                        bot_city = random.choice([i for i in cities_list if i.startswith(last_letter) and i not in user_data[user]])  # выбираем рандомный город, который начинается с последней буквы
                        update.message.reply_text(bot_city)  # отвечаем городом
                        user_data[user].append(bot_city)  # добавляем город в список


def wordcount(update, context):
    user_text = str(update.message.text[10:])
    print(user_text)
    if len(user_text) == 0:
        update.message.reply_text('Что мне считать, если ты мне отправил пустоту?')
    else:
        update.message.reply_text(f"Количество слов: {len(re.findall('[a-zA-Zа-яА-Я_]+', user_text))}")


def calc(update, context):
    user = update.message.from_user.username
    try:
        user_text = str(update.message.text).split()[-1]
        if ',' in user_text:
            user_text = user_text.replace(',', '.')

        if re.findall('(\d+).+?(\d+)', user_text):
            update.message.reply_text(f"Ответ: {eval(user_text)}")
        else:
            update.message.reply_text(f"Что-то ты мне прислал ерунду какую-то.\n"
                                      f"Пиши /calc и пример, который должен решить, а не вот это вот все.\n")
    except TypeError:
        update.message.reply_text(f"Не понимаю как это решить. Попробуй написать пример по-другому.")
    except ZeroDivisionError:
        update.message.reply_text(f"Себя на 0 подели. Школьную математику забыл?")
    except SyntaxError:
        update.message.reply_text(f"У тебя в примере, это... Ошибка есть. Давай по новой, {user}.")


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
    dp.add_handler(CommandHandler("game", city_game))
    dp.add_handler(CommandHandler("wordcount", wordcount))
    dp.add_handler(CommandHandler("calc", calc))
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
