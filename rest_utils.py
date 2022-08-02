import os
import json
import logging

from typing import List

from tinkoff.invest import Client, InstrumentIdType

import config

file_name = config.file_name
TOKEN = config.TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_instrument(ticker: str) -> bool:
    if os.path.getsize(file_name) == 0:
        return True
    with open(file_name) as file:
        data = json.load(file)
        if ticker in data.keys():
            return False
        else:
            return True


def add_new_instruments():
    if not os.path.exists(file_name):
        open(file_name, 'w+')
        logging.info(f'Файл {file_name} успешно создан')
    share_figi = {}
    print("Что бы добавить новый инструмент введите их")
    while True:
        ticker = input().strip().upper()
        if ticker:
            if check_instrument(ticker):
                with Client(TOKEN) as client:
                    share = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,class_code='SPBXM', id=ticker)
                    share_figi[ticker] = share.instrument.figi
            else:
                print(f'Тикер {ticker} уже добвален')
                logging.info(f'Тикер {ticker} уже добвален')
        else:
            if len(share_figi.keys()) == 0:
                logging.info('Ни одного тикера добавлено не было')
                break
            else:
                with open(file_name, 'w') as file:
                    json.dump(share_figi, file)
                    logging.info(f'Тикеры {share_figi.keys()} записаны в файл {file_name}')
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

    return fav


def get_figi(ticker: str) -> str:
    with Client(TOKEN) as client:
        return client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code='SPBXM', id=ticker).instrument.figi