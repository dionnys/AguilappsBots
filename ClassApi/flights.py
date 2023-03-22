import requests

class AviationAPIs:
    flightaware_key = 'your_flightaware_key'
    aviationstack_key = 'your_aviationstack_key'
    opensky_key = 'your_opensky_key'
    airportinfo_key = 'your_airportinfo_key'
    weather_key = 'your_weather_key'
    flightstats_app_id = 'your_flightstats_app_id'
    flightstats_app_key = 'your_flightstats_app_key'

    @classmethod
    def flightaware_api(cls, flight_number):
        url = f'https://flightxml.flightaware.com/json/FlightXML3/FlightInfoStatus?ident={flight_number}'
        response = requests.get(url, auth=(cls.flightaware_key, ''))
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    @classmethod
    def aviationstack_api(cls, dep_iata, arr_iata, flight_status):
        url = 'http://api.aviationstack.com/v1/flights'
        params = {
            'access_key': cls.aviationstack_key,
            'dep_iata': dep_iata,
            'arr_iata': arr_iata,
            'flight_status': flight_status
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    @classmethod
    def opensky_api(cls, icao24):
        url = f'https://opensky-network.org/api/states/all?icao24={icao24}&lamin=40.0&lomin=-10.0&lamax=60.0&lomax=40.0'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    @classmethod
    def airportinfo_api(cls, airport_code):
        url = f'https://airportinfo.p.rapidapi.com/airport?icao={airport_code}'
        headers = {
            'X-RapidAPI-Key': cls.airportinfo_key
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    @classmethod
    def weather_api(cls, airport_code):
        url = f'https://api.weather.gov/stations/{airport_code}/observations/latest'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    @classmethod
    def flightstats_api(cls, flight_number, year, month, day):
        url = f'https://api.flightstats.com/flex/flightstatus/rest/v2/json/flight/status/{flight_number}/dep/{year}/{month}/{day}?appId={cls.flightstats_app_id}&appKey={cls.flightstats_app_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None