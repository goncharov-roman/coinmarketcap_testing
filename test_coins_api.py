import requests
import json
import datetime

def test_coin_service():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '10',
        'sort': 'volume_24h',
        'sort_dir': 'desc'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'XXX'
    }

    try:
        resp = requests.get(url, params=parameters, headers=headers)
        data = json.loads(resp.text)

        assert resp.status_code == 200
        assert data["status"]["elapsed"] < 500
        assert len(resp.content) < 10 * 1024

        for item in data["data"]:
            assert datetime.datetime.strptime(item["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ").date() == datetime.datetime.now().date()
    except (ConnectionError, TimeoutError) as e:
        print(e)

# date stuff
#print(datetime.datetime.now().date())
#print(datetime.datetime.strptime("2020-06-29T08:13:29.303Z", "%Y-%m-%dT%H:%M:%S.%fZ").date())
