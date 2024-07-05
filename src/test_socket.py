import json
import random
import time

import requests

while True:
    url1 = "http://0.0.0.0/v1/FC28/create"
    data1 = {
        "soil_moisture": random.randint(10, 20)
    }
    res1 = requests.post(
        url=url1,
        data=json.dumps(data1)
    )
    time.sleep(0.7)
    url2 = "http://0.0.0.0/v1/DHT11/create"
    data2 = {
        "temperature": random.randint(10, 20),
        "air_humidity": random.randint(10, 20),
    }
    res2 = requests.post(
        url=url2,
        data=json.dumps(data2)
    )
    print(f"res1 status: {res1}, res2 status: {res2}")
    time.sleep(0.3)

