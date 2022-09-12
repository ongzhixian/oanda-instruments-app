
import json
import logging

from datetime import datetime
from os import path
from urllib.parse import quote
from urllib.request import urlopen as url_open
from urllib.request import Request as url_request

import pika

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
# └───fetch.oanda.price
#     └───fetch_oanda_price

EXCHANGE_NAME = 'financial_instrument'
ROUTING_KEY = "fetch.oanda.price"
QUEUE_NAME = 'fetch_oanda_price'


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
    log.info(f"Rows affected {rows_affected}")


def get_instrument_code_list(sgx_isin_data_rows):
    return [ 'XCU_USD', 'EUR_USD', 'USD_JPY' ]
    

def setup_rabbit_mq(channel):
    channel.exchange_declare(
        exchange=EXCHANGE_NAME, 
        exchange_type='topic')
        
    channel.queue_declare(
        queue=QUEUE_NAME, 
        durable=True)
    
    channel.queue_bind(
        exchange=EXCHANGE_NAME, 
        routing_key=ROUTING_KEY,
        queue=QUEUE_NAME)


def publish_tickers(url_parameters, ticker_list):

    with pika.BlockingConnection(url_parameters) as connection, connection.channel() as channel:

        setup_rabbit_mq(channel)

        for ticker in ticker_list:

            channel.basic_publish(
                exchange=EXCHANGE_NAME, 
                routing_key=ROUTING_KEY, 
                body=ticker,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ))

            log.info(f"Publish {ticker}", event="publish", type="ticker", target=ticker)
        

if __name__ == "__main__":
    log = setup_logging()
    (url_parameters, database_settings, oanda_settings, output_path) = get_settings_from_arguments()
    oanda_api = OandaApi(oanda_settings, output_path)
    trading_instruments = oanda_api.get_account_instruments()
    
    store_account_instruments_to_database(trading_instruments)

    instrument_code_list = get_instrument_code_list(trading_instruments)
    publish_tickers(url_parameters, instrument_code_list)

    log.info("Program complete", source="program", event="complete")
