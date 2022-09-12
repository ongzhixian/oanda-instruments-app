
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
from oanda_api import OandaApi
from data_providers import MySqlDataProvider

"""
1.  This download instruments from API.
2.  It then parses the list for tickers.
3.  Tickers are then written to the queue.
"""


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

def store_account_instruments_to_database(instruments):
    mysql = MySqlDataProvider(database_settings['financial'])
    market_identifier_id = 'OANDA'
    sql = """
INSERT INTO instrument (market_identifier_id, code, name, counter)
SELECT  %s      AS 'market_identifier_id'
        , %s    AS 'code'
        , %s    AS 'name'
        , %s    AS 'counter'
FROM    (SELECT 1) a
WHERE NOT EXISTS (SELECT 1 FROM instrument WHERE market_identifier_id = %s AND code = %s)
LIMIT 1;
"""
    data_rows = [(market_identifier_id, x['name'], x['displayName'], x['name'], market_identifier_id, x['name']) for x in instruments]
    (rows_affected, errors) = mysql.execute_batch(sql, data_rows)
    log.info("Rows affected {rows_affected}")

if __name__ == "__main__":
    log = setup_logging()
    (url_parameters, database_settings, oanda_settings, output_path) = get_settings_from_arguments()
    oanda_api = OandaApi(oanda_settings, output_path)
    trading_instruments = oanda_api.get_account_instruments()
    
    store_account_instruments_to_database(trading_instruments)

    log.info("Program complete", source="program", event="complete")
