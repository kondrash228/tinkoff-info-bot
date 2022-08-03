import os
import json
import logging

from typing import List

from tinkoff.invest import Client, InstrumentIdType

import config

file_name = config.file_name
TOKEN = config.TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_instrument_type() -> str:
    print('Какой тип инструмента вы хотите добваить?\nАкция - 1\nФонд - 2\nФьючерс - 3')
    instrument_type = int(input())

    if instrument_type == 1:
        logging.info('Тип инструмента share')
        return 'share'

    if instrument_type == 2:
        logging.info('Тип инструмента etf')
        return 'etf'

    if instrument_type == 3:
        logging.info('Тип инструмента future')
        return 'future'


def check_instrument(ticker: str) -> bool:
    if os.path.getsize(file_name) == 0:
        return True
    with open(file_name) as file:
        data = json.load(file)
        if ticker in data.keys():
            logging.info('Тикер уже присутсвует')
            return False
        else:
            logging.info('Тикера нет в избранном')
            return True


def add_new_instruments():
    if not os.path.exists(file_name):
        open(file_name, 'w+')
        logging.info(f'Файл {file_name} успешно создан')
    else:
        with open(file_name) as json_file:
            data: dict = json.load(json_file)
        logging.info(f'Файл {file_name} прочитан {data}')
        stock_figi = {}
        print("Что бы добавить новый инструмент введите их")

        instrument_type = get_instrument_type()

        while True:
            ticker = input().strip().upper()
            if ticker:
                if check_instrument(ticker):
                    with Client(TOKEN) as client:
                        if instrument_type == 'share':
                            figi = get_figi(ticker)
                            class_code = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi).instrument.class_code
                            stock = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                                class_code=class_code, id=ticker)
                        if instrument_type == 'etf':
                            figi = get_figi(ticker)
                            class_code = client.instruments.etf_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                                                                     id=figi).instrument.class_code
                            stock = client.instruments.etf_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                              class_code=class_code, id=ticker)
                        if instrument_type == 'future':
                            figi = get_figi(ticker)
                            class_code = client.instruments.future_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                                                                   id=figi).instrument.class_code
                            stock = client.instruments.future_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                                 class_code=class_code, id=ticker)

                        stock_figi[ticker] = stock.instrument.figi
                        data[ticker] = stock.instrument.figi
                        logging.info(f'Инструменты добавлены {stock_figi}')
                else:
                    print(f'Тикер {ticker} уже добвален')
                    logging.info(f'Тикер {ticker} уже добвален')
            else:
                if len(stock_figi.keys()) == 0:
                    logging.info('Ни одного тикера добавлено не было')
                    break
                else:
                    with open(file_name, 'w') as file:
                        json.dump(data, file)
                        logging.info(f'Тикеры {stock_figi.keys()} записаны в файл {file_name}')
                        break


def get_last_prices() -> dict:
    info = {}
    with Client(TOKEN) as client:
        with open(file_name) as json_file:
            data: dict = json.load(json_file)

            for ticker, figi in data.items():
                get_last_price = client.market_data.get_last_prices(figi=[figi])

                for last_price in get_last_price.last_prices:
                    info[ticker] = last_price.price.units + (last_price.price.nano / pow(10, 9))
    logging.info(f'Последние цены успешно получены {info}')
    return info


def get_favourites() -> List[str]:
    fav = []
    with open(file_name) as json_file:
        data: dict = json.load(json_file)

        for ticker in data.keys():
            fav.append(ticker)
    logging.info(f'Запрос избранного {fav}')
    return fav


def get_figi(ticker: str) -> str:
    with Client(TOKEN) as client:
        instrument = client.instruments.find_instrument(query=ticker)
        for data in instrument.instruments:
            logging.info(f'Запрос figi {data.figi}')
            return data.figi

