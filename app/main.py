"""
1.  This download instruments from API.
2.  It then parses the list for tickers.
3.  Tickers are then written to the queue.
"""

import json
import logging

from datetime import datetime
from os import path
from urllib.parse import quote
from urllib.request import urlopen as url_open
from urllib.request import Request as url_request

# import pika

from logger import Logger
from program_arguments import get_settings_from_arguments


# 
# financial_instrument
# └───fetch.yahoo-finance.price
#     └───fetch_yahoo_finance_price

EXCHANGE_NAME = 'financial_instrument'
ROUTING_KEY = "yafi.fetch"
QUEUE_NAME = 'yafi_fetch'


def setup_logging():
    logging.getLogger('pika').setLevel(logging.WARNING)
    log = Logger()
    return log


if __name__ == "__main__":
    log = setup_logging()
    (url_parameters, database_settings, output_path) = get_settings_from_arguments()
    # listen_for_tickers(url_parameters)
    log.info("Program complete", source="program", event="complete")
