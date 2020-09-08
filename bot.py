import logging
import ephem
from mybot import settings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# PROXY = {'proxy_url': settings.PROXY_URL,
#     'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

'''Если понадобиться включить прокси, просто раскоммнетировать 5 и 6 строку и в переменную mybot ниже
добавить аргумент request_kwargs=PROXY'''

logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S'
                    )


def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь! Ты вызвал команду /start')


def coord(update, context):
    user_text = str(update.message.text.split()[1])
    date = ephem._datetime.utcnow()
    if user_text == 'mercury':
        update.message.reply_text(ephem.constellation(ephem.Mercury(date)))
    elif user_text == 'venus':
        update.message.reply_text(ephem.constellation(ephem.Venus(date)))
    elif user_text == 'mars':
        update.message.reply_text(ephem.constellation(ephem.Mars(date)))
    elif user_text == 'jupiter':
        update.message.reply_text(ephem.constellation(ephem.Jupiter(date)))
    elif user_text == 'saturn':
        update.message.reply_text(ephem.constellation(ephem.Saturn(date)))
    elif user_text == 'uranus':
        update.message.reply_text(ephem.constellation(ephem.Uranus(date)))
    elif user_text == 'neptune':
        update.message.reply_text(ephem.constellation(ephem.Neptune(date)))
    else:
        update.message.reply_text('Запрос неверен.')


def talk_to_me(update, context):
    user_text = update.message.text
    logging.info(user_text)
    print(user_text)
    update.message.reply_text(user_text)


def main():
    # Создаем бота и передаем ему ключ для авторизации на серверах Telegram
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", coord))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал!')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()


if __name__ == '__main__':
    main()
