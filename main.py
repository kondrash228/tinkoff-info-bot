import logging
import telebot
from tinkoff.invest import Client

import config
from rest_utils import get_last_prices, add_new_instruments, get_favourites, get_figi

TG_TOKEN = config.TG_TOKEN
TOKEN = config.TOKEN

bot = telebot.TeleBot(token=TG_TOKEN)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@bot.message_handler(commands=['start'])
def main(message: telebot.types.Message):
    bot.send_message(message.chat.id,
                     'Добро пожаловать, для того что бы посмотреть актуальные котировки нажмите /get_prices')


@bot.message_handler(commands=['get_prices'])
def show_data(message: telebot.types.Message):
    last_prices = get_last_prices()
    if len(last_prices) > 0:
        text = ''
        for ticker, price in last_prices.items():
            text += f'[{ticker}](https://www.tinkoff.ru/invest/stocks/{ticker}/) - {price}$ [график](https://stockcharts.com/c-sc/sc?s={ticker}&p=D&b=5&g=0&i=0&r=1659368752842.img)\n'
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Не добавлено ни одного стикера')


@bot.message_handler(commands=['trade'])
def trade(message: telebot.types.Message):
    favourite_tickers = get_favourites()
    text = ''
    for i in range(len(favourite_tickers)):
        text += f'{favourite_tickers[i]} - {i}\n'

    bot.send_message(message.chat.id, f'ИЗБРАННОЕ\n{text}')
    bot.send_message(message.chat.id, 'Что бы начать записывать данные выберете из списка желаемую акцию')
    bot.register_next_step_handler(message, start_streaming)


def start_streaming(message: telebot.types.Message):
    bot.send_message(message.chat.id, f'Вы выбрали акцию - {get_favourites()[int(message.text)]}')
    # with Client(TOKEN) as client:
    #     order_book = client.market_data.get_order_book(figi=get_figi(favourite_tickers[0]), depth=1)
    #
    #     bids = order_book.bids[0].price.units + (order_book.bids[0].price.nano / pow(10, 9))
    #     asks = order_book.asks[0].price.units + (order_book.asks[0].price.nano / pow(10, 9))
    #
    #     bids_quantity = order_book.bids[0].quantity
    #     asks_quantity = order_book.asks[0].quantity

    # bot.send_message(message.chat.id,f'[bids]: {bids}\t[quantity]: {bids_quantity}\n[asks]: {asks}\t[quantity]: {asks_quantity}')


@bot.message_handler(commands=['streaming'])
def order_book_streaming(message: telebot.types.Message):
    pass


@bot.message_handler()
def main(message: telebot.types.Message):
    logging.info(f'MAIN: {message.text}')


if __name__ == '__main__':
    try:
        print('что бы добавить инструмент введите - 1, что бы начать пользоваться ботом введите 2')
        choice = int(input())
        if choice == 1:
            logging.info('Бот рабоатет')
            add_new_instruments()
            bot.polling()
        else:
            logging.info('Бот рабоатет')
            bot.polling()
    except KeyboardInterrupt:
        pass
