from datetime import datetime
from dotenv import load_dotenv
import logging

### We import the different chamber scrapping scripts

from chambers.canada import get_canada
from chambers.spain import get_spain
from chambers.sweden import get_sweden
from chambers.switzerland import get_switzerland
from chambers.italy import get_italy
from chambers.deutschland import get_deutschland
from chambers.france import get_france
from chambers.belgium import get_belgium
from chambers.uk import get_uk
from chambers.us import get_us

### We import the utilities

from utilities import country_chambers

## We load the environmental functions
load_dotenv()

def clear_older_events(events):
    for event in events:
        try:
            if datetime.strptime(event["date"], "%Y-%m-%d") < datetime.now():
                events.remove(event)
        except Exception as e:
            print(f"Error fetching events: {e}")
            pass
    return



## Event Crawler class

def get_countries(country_url, country_url_sel):

    # Variable para ejecutar una cámara determinada (desmarcar y completar if needed)
    # country_url = {"Italy": "https://iccj.or.jp/upcoming-events/"}
    events = []

    for key, value in country_url.items():
        url = value
        country = key

        if country == "Canada":
            try:
                get_canada(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting Canada events: %s", err)
                pass
        elif country == "Spain":
            try:
                get_spain(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting Spain events: %s", err)
                pass
        elif country == "Sweden":
            try:
                get_sweden(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting Sweden events: %s", err)
                pass
        elif country == "Switzerland":
            try:
                get_switzerland(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting Swiss events: %s", err)
                pass
        elif country == "Italy":
            try:
                get_italy(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting Italy events: %s", err)
                pass
        elif country == "Deutschland":
            try:
                get_deutschland(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting German events: %s", err)
                pass
        elif country == "France":
            try:
                get_france(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting France events: %s", err)
                pass
        elif country == "Belgium":
            try:
                get_belgium(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting Belgium events: %s", err)
                pass
        else:
            print(f"Country {country} has not been defined in the scrapping or there is a misspelling letter")


    for key, value in country_url_sel.items():
        url = value
        country = key

        if country == "UK":
            try:
                get_uk(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting UK events: %s", err)
                pass
        elif country == "US":
            try:
                get_us(url, country, events, country_chambers)
            except Exception as err:
                logging.error("Error while getting US events: %s", err)
                pass
        else:
            print(f"Country {country} has not been defined in the selenium scrapping or there is a misspelling letter")

    clear_older_events(events)

    return events