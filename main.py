import os
import urllib.request
import urllib.parse
import json
import sched
import time
import logging
from random import randrange

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s')

try:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
    CONFIG = json.load(open(CONFIG_PATH, 'r'))
except FileNotFoundError:
    logging.info('No config file found')
    quit()

TINKOFF_API = CONFIG['tinkoffAPI']
BOT_TOKEN = CONFIG['botToken']
CHAT_ID = CONFIG['chatID']
TIMEOUT = CONFIG['timeout']
SHED = sched.scheduler(time.time, time.sleep)


def send_currency_rates():
    with urllib.request.urlopen(TINKOFF_API) as data:
        data = json.loads(data.read())

        for item in data['payload']['rates']:
            if item['category'] == 'DebitCardsTransfers':
                rates = f"RUB—TENGE \nBUY: {item['buy']} | SELL: {item['sell']}"
                rates = urllib.parse.quote_plus(rates)

                bot_api = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={rates}'
                with urllib.request.urlopen(bot_api) as message:
                    logging.info(f"BUY: {item['buy']} | SELL: {item['sell']}")


def shedHandler():
    logging.info(f'CurrencyRates script started')
    send_currency_rates()
    SHED.enter(TIMEOUT + randrange(300), 1, shedHandler)


try:
    SHED.enter(1, 1, shedHandler)
    SHED.run()
except KeyboardInterrupt:
    pass
