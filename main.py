import os
import json
import sched
import time
import logging
import urllib.request
import urllib.parse
from random import choice


def get_currency_rates(currencies: list) -> str:
    result = 'Debit Cards Transfers\n'

    for currency in currencies:
        with urllib.request.urlopen(currency) as data:
            data = json.loads(data.read())

            for item in data['payload']['rates']:
                if item['category'] == 'DebitCardsTransfers':
                    from_currency = item['fromCurrency']['name']
                    to_currency = item['toCurrency']['name']
                    if from_currency == 'RUB':
                        result += (f"\n1 {from_currency} = {item['buy']} {to_currency}\n"
                                   f"BUY: {item['buy']} | SELL: {item['sell']}\n")
                    else:
                        result += (f"\n1 {from_currency} = {item['sell']} {to_currency}\n"
                                   f"BUY: {item['sell']} | SELL: {item['buy']}\n")
    return result


def send_message(bot_token: str, chat_id: str, message: str) -> None:
    bot_api = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'

    with urllib.request.urlopen(bot_api) as message:
        data = json.loads(message.read())
        logging.info(f"Message sent: {data['ok']}")


def shedHandler(old_message: str, config: dict) -> None:
    scheduler = sched.scheduler(time.time, time.sleep)
    message = get_currency_rates(config['currencies'])
    delay = config['interval'] + config['spread'] * choice([-1, 1])

    if message != old_message:
        send_message(config['botToken'], config['chatID'],
                     urllib.parse.quote(message))
        old_message = message
    else:
        logging.info('No changes')

    scheduler.enter(delay, 1, shedHandler, argument=(old_message, config,))
    scheduler.run()


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(levelname)s | %(message)s')

    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        config = json.load(open(config_path, 'r'))
    except FileNotFoundError:
        logging.info('No config file found')
        quit()

    try:
        logging.info(f'CurrencyRates script started')
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(1, 1, shedHandler, argument=('', config,))
        scheduler.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
