import json

from datetime import datetime
from os import path, makedirs
from urllib.request import urlopen as url_open
from urllib.request import Request as url_request

from logger import Logger

log = Logger()

class OandaApi(object):
    def __init__(self, settings, output_path):
        self.account_id = settings['account_number']
        self.api_key = settings['api_key']
        self.rest_api_url = settings['rest_api_url']
        self.streaming_api_url = settings['streaming_api_url']
        self.output_path = output_path
        self.headers={
            'Authorization': f"Bearer {self.api_key}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'
        }
        required_sub_directories = [ 'instruments' ]
        for sub_directory in required_sub_directories:
            directory_path = path.join(self.output_path, sub_directory)
            full_path = path.abspath(directory_path)
            if not path.exists(full_path):
                try:
                    makedirs(full_path)
                except Exception:
                    log.error(f"ERROR - output path does not exists {full_path}")
                    exit(2)


    def save_data_to_file(self, data):
        FILE_DATETIME = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        FILE_NAME = f'instruments-{FILE_DATETIME}.txt'
        SAVE_FILE_PATH = path.join(self.output_path, 'instruments', FILE_NAME)
        with open(SAVE_FILE_PATH, 'w', encoding='utf-8') as out_file:
            out_file.write(data)

    def get_account_instruments(self):
        """
        Get account instruments
        """
        account_id = self.account_id
        url = f"{self.rest_api_url}/v3/accounts/{account_id}/instruments"

        request = url_request(
            url, 
            data=None, 
            headers=self.headers
        )
        with url_open(request) as response:
            response_data = response.read().decode("utf-8")
            self.save_data_to_file(response_data)
        try:
            response_json = json.loads(response_data)
            return response_json['instruments'] if 'instruments' in response_json else []
        except Exception as ex:
            log.warn(f"Invalid response_json; {ex}")
            return []
