import json

import requests

from data_processing.scrapers.lunarcrush.headers import google_api_headers, get_headers


def get_google_auth():

    key = "AIzaSyBAMtbrsRL6tnE_INeT7l04U2CjzeRhb3w"

    url = f'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={key}'

    data = {"email": "di.matoschaves@gmail.com", "password": "Olissipo1986!", "returnSecureToken": True}

    r = requests.post(url, headers=google_api_headers, json=data)

    response = r.json()

    return response["idToken"]


def get_session_key():

    bearer_token = get_google_auth()

    data = {'data':{'data':'assets','symbol':'btc','data_points':10,'interval':'hour'}}

    headers = get_headers(bearer_token)

    url = 'https://us-central1-coin-insights.cloudfunctions.net/apiRequest'

    r = requests.post(url, headers=headers, data=json.dumps(data))

    response = r.json()

    return response["result"]["config"]["set_tmp_user_token"]


if __name__ == '__main__':
    response = get_session_key()
