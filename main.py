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

CURRENCIES = CONFIG['currencies']
BOT_TOKEN = CONFIG['botToken']
CHAT_ID = CONFIG['chatID']
TIMEOUT = CONFIG['timeout']
SHED = sched.scheduler(time.time, time.sleep)


def send_currency_rates():
    result = ''

    for currency in CURRENCIES:
        with urllib.request.urlopen(currency) as data:
            data = json.loads(data.read())

            for item in data['payload']['rates']:
                if item['category'] == 'DebitCardsTransfers':
                    from_currency = item['fromCurrency']['name']
                    to_currency = item['toCurrency']['name']
                    result += f"\n{from_currency} | {to_currency}\nBUY: {item['buy']} | SELL: {item['sell']}\n"

    result = urllib.parse.quote(result)
    bot_api = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={result}'

    with urllib.request.urlopen(bot_api) as message:
        data = json.loads(message.read())
        logging.info(f"Message sent: {data['ok']}")


def shedHandler():
    send_currency_rates()
    SHED.enter(TIMEOUT + randrange(300), 1, shedHandler)


try:
    logging.info(f'CurrencyRates script started')
    SHED.enter(1, 1, shedHandler)
    SHED.run()
except KeyboardInterrupt:
    pass
