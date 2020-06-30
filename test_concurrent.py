import datetime
import json
import queue
import math
import requests
import threading
import time

#from test_coins_api import test_coin_service
queue_results = queue.Queue()

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
        'X-CMC_PRO_API_KEY': '0d997c8f-1229-4720-a95b-2c398a244e18'
    }

    try:
        resp = requests.get(url, params=parameters, headers=headers)
        data = json.loads(resp.text)

        if resp.status_code == 200:
            coin_dates = []
            for item in data["data"]:
                coin_dates.append(datetime.datetime.strptime(item["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ").date())
            queue_results.put([data["status"]["elapsed"], len(resp.content), coin_dates, resp.status_code])

        #for item in data["data"]:
        #    assert datetime.datetime.strptime(item["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ").date() == datetime.datetime.now().date()
    except (ConnectionError, TimeoutError) as e:
        queue_results.put('exc', resp.elapsed.total_seconds())

def percentile(N, percent, key=lambda x: x):
    if not N:
        return None

    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0 + d1


def test_concurrent():
    concurrent_users = 8
    workers = []

    start_time = time.time()
    for i in range(concurrent_users):
        thread = threading.Thread(target=test_coin_service(), daemon=True)
        thread.start()
        workers.append(thread)

    for w in workers:
        w.join()
    end_time = time.time()

    qsize = queue_results.qsize()
    total_pass_requests = 0
    total_time = 0
    times = []

    for i in range(qsize):
        try:
            result = queue_results.get_nowait()
        except Empty:
            break
        
        total_pass_requests += 1
        total_time += result[0] * 0.001
        times.append(result[0])
        assert result[0] < 500
        assert result[1] < 10 * 1024
        for item in result[2]:
            assert item == datetime.datetime.now().date()
        assert result[3] == 200

    #tested_time = end_time - start_time
    rps_mean = total_pass_requests / total_time

    assert rps_mean > 5
    assert percentile(sorted(times), 0.8) < 450