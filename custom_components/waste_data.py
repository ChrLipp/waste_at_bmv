import logging
import ssl

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from homeassistant.util import Throttle
import requests

_LOGGER = logging.getLogger(__name__)
MIN_TIME_BETWEEN_UPDATES = timedelta(days=1)

# Fetches and provides the waste data.
class WasteData:

    def __init__(self, ort, strasse, hausnummer):
        _LOGGER.debug("WasteSensor ctor")
        self.restmuell = None
        self.gelberSack = None
        self.papier = None
        self.ort = ort
        self.strasse = strasse
        self.hausnummer = hausnummer

    # Checks if the given string is a valid date in the future (or today).
    # Parses the  date from the html which is something like "Donnerstag, 11.11.2021"
    # and convert it to date
    def parse_date(self, date_string):
        result: date = None
        if ', ' in date_string:
            parts = date_string.split(', ')
            parsed_date = datetime.strptime(parts[1], '%d.%m.%Y').date()
            if parsed_date >= date.today():
                result = parsed_date
        return result

    # Select all date entries
    def get_text_from_tds(self, elements):
        result = list()
        for element in elements:
            parsed_date = self.parse_date(element.select('p')[0].text)
            if parsed_date is not None:
                result.append(parsed_date)
        return result

    # Calls the servlet with the given parameters.
    def get_servlet(self, parms):
        # build URI on given parameters
        servlet_url = 'https://webudb.udb.at/WasteManagementUDB/WasteManagementServlet'

        # set headers
        headers = {
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
        }

        # execute request
        resp = requests.get(servlet_url, params=parms, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup

    # Fetches the waste data
    def fetch_data(self):
        # call 1, get session id
        params1 = {
            'SubmitAction': 'wasteDisposalServices',
            'InFrameMode': 'TRUE'
        }
        doc = self.get_servlet(params1)
        form_session = doc.select('form #SessionId')[0]

        # call 2, ask for the dates
        params1['SubmitAction'] = 'abfTermBMV'
        doc = self.get_servlet(params1)

        # call 3, set address data
        paramsMap = {
            'SubmitAction': 'changedEvent',
            'InFrameMode': 'TRUE',
            'Ort': self.ort,
            'Strasse': self.strasse,
            'Hausnummer': self.hausnummer,
            'ApplicationName': 'com.athos.kd.udb.CheckAbfuhrTermineParameterBusinessCase',
            form_session['name']: form_session['value']
        }
        doc = self.get_servlet(paramsMap)

        # call 4, finalize
        paramsMap['SubmitAction'] = 'forward'
        doc = self.get_servlet(paramsMap)

        # Parses the dates from the html
        restmuellSelection = doc.find("ul", {"id": "TermineR"}).select('li')
        self.restmuell = self.get_text_from_tds(restmuellSelection)

        gelberSackSelection = doc.find("ul", {"id": "TermineL"}).select('li')
        self.gelberSack = self.get_text_from_tds(gelberSackSelection)

        papierSelection = doc.find("ul", {"id": "TermineP"}).select('li')
        self.papier = self.get_text_from_tds(papierSelection)
        
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.force_update()

    def force_update(self):
        _LOGGER.info("Updating waste dates using remote API")
        self.fetch_data()
