import json
import telebot
from typing import List
from tinkoff.invest import Client, InstrumentIdType

import config

TOKEN = config.TOKEN
TG_TOKEN = config.TG_TOKEN
shares = config.shares
file_name = config.file_name

bot = telebot.TeleBot(token=TG_TOKEN)


def add_figis_to_file(tickers: List[str]) -> None:
    share_figi = {}
    with Client(TOKEN) as client:
        for tick in tickers:
            share = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code='SPBXM',
                                                id=tick)
            share_figi[tick] = share.instrument.figi
        with open(file_name, 'w') as file:
            json.dump(share_figi, file)


def get_last_prices() -> dict:
    info = {}
    with Client(TOKEN) as client:
        with open(file_name) as json_file:
            data: dict = json.load(json_file)

            for ticker, figi in data.items():
                get_last_price = client.market_data.get_last_prices(figi=[figi])

                for last_price in get_last_price.last_prices:
                    info[ticker] = last_price.price.units + (last_price.price.nano / pow(10, 9))
    return info


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id,'Добро пожаловать, для того что бы посмотреть актуальные котировки нажмите /get_prices')


# (https://www.tinkoff.ru/invest/stocks/{ticker}/) (https://stockcharts.com/c-sc/sc?s={ticker}&p=D&b=5&g=0&i=0&r=1659368752842)

@bot.message_handler(commands=['get_prices'])
def show_data(message):
    last_prices = get_last_prices()
    text = ''
    for ticker, price in last_prices.items():
        text += f'[{ticker}](https://www.tinkoff.ru/invest/stocks/{ticker}/) - {price}$ [график](https://stockcharts.com/c-sc/sc?s={ticker}&p=D&b=5&g=0&i=0&r=1659368752842.img)\n'
    bot.send_message(message.chat.id, text, parse_mode='Markdown')


if __name__ == '__main__':
    add_figis_to_file(shares)
    bot.polling()
