import os
import urllib.request
import urllib.parse
import json
import sched
import time
import logging
from random import choice, randrange

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
INTERVAL = CONFIG['interval']
SPREAD = CONFIG['spread']
SCHED = sched.scheduler(time.time, time.sleep)


def get_currency_rates(currencies) -> str:
    result = 'Debit Cards Transfers\n'

    for currency in currencies:
        with urllib.request.urlopen(currency) as data:
            data = json.loads(data.read())

            for item in data['payload']['rates']:
                if item['category'] == 'DebitCardsTransfers':
                    from_currency = item['fromCurrency']['name']
                    to_currency = item['toCurrency']['name']
                    if from_currency == 'RUB':
                        result += f"\n1 {from_currency} = {item['buy']} {to_currency}\nBUY: {item['buy']} | SELL: {item['sell']}\n"
                    else:
                        result += f"\n1 {from_currency} = {item['sell']} {to_currency}\nBUY: {item['sell']} | SELL: {item['buy']}\n"
    return result


def send_message(bot_token: str, chat_id: str, bot_message: str) -> None:
    bot_api = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={bot_message}'

    with urllib.request.urlopen(bot_api) as message:
        data = json.loads(message.read())
        logging.info(f"Message sent: {data['ok']}")


def shedHandler(prev_bot_message) -> None:
    bot_message = get_currency_rates(CURRENCIES)
    delay = INTERVAL + randrange(SPREAD) * choice([-1, 1])

    if bot_message != prev_bot_message:
        send_message(BOT_TOKEN, CHAT_ID, urllib.parse.quote(bot_message))
        prev_bot_message = bot_message
    else:
        logging.info('No changes')

    SCHED.enter(delay, 1, shedHandler, argument=(prev_bot_message,))


try:
    logging.info(f'CurrencyRates script started')
    SCHED.enter(1, 1, shedHandler, argument=('',))
    SCHED.run()
except KeyboardInterrupt:
    pass
