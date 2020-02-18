import pandas as pd
import requests

ENDPOINT_URL = 'http://localhost:8880/api/climate/'
DATA_FILE = 'data/climate.csv'

def send_record(data):
    r = requests.post(
        ENDPOINT_URL,
        json=data,
        auth=requests.auth.HTTPBasicAuth('admin', 'password')
    )
    if r.status_code == 200:
        print(f'Ok for {data.id}')
    else:
        print(f'Got {r.status_code}')
        print(r.content)

#   "station_name": "ABEE AGDM",
#   "climate_id": "3010010",
#   "province_code": "AB",
#   "local_date": "2020-01-01 00:00:00",
#   "mean_temp": "string",
#   "min_temp": 0,
#   "max_temp": 0,
#   "record_id": 0
def iterate_data():
    cdf = pd.read_csv(DATA_FILE)
    for i in range(1) : 
        to_send = {
            "station_name": cdf.loc[i, "STATION_NAME"],
            "climate_id": cdf.loc[i, "CLIMATE_IDENTIFIER"],
            "province_code": cdf.loc[i, "PROVINCE_CODE"],
            "local_date": cdf.loc[i, "LOCAL_DATE"],
            "mean_temp": float(cdf.loc[i, "MEAN_TEMPERATURE"]),
            "min_temp": float(cdf.loc[i, "MIN_TEMPERATURE"]),
            "max_temp": float(cdf.loc[i, "MAX_TEMPERATURE"]),
            "record_id": cdf.loc[i, "ID"]
        }
        send_record(data=to_send)

iterate_data()