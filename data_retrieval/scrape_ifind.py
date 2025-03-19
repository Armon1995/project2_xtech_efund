"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu & guozhanglong

E-mail: davide97ls@gmail.com

Goal: Scrape iFind data
"""
import requests
import json
import pandas as pd
from datetime import datetime
from keys import ifind_key

pd.set_option('float_format', lambda x: '%.2f' % x)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 500)

ths_headers = {"Content-Type": "application/json",
               "access_token": ifind_key}

id_list = ['L004609506', 'L015211473', 'M002834227', 'M002807951', 'L001618703', 'L001618528', 'L001619976',
           'L001618529', 'L001619517', 'L001619472', 'L001618704', 'L001618530', 'L001618705', 'L001619708',
           'L001619518', 'L001620156', 'L001618706', 'L001618531', 'S002984302', 'M012197497', 'M002890476',
           'M006516243', 'M006731641', 'M002043802', 'M003026383', 'M001624503', 'M002807943', 'M006536828',
           'M002807951', 'M004490200', 'M004339251', 'M003009996',
           'L001619493', 'L015211422', 'M002816549',
]


def edb(id_, startdate='2024-05-01', enddate='2025-02-25'):
    """
    Fetches data from the EDB service based on the given ID, start date, and end date.

    Args:
        id_ (str): The ID of the indicator to fetch data for.
        startdate (str): The start date for the data (format: 'YYYY-MM-DD').
        enddate (str): The end date for the data (format: 'YYYY-MM-DD').

    Returns:
        bytes: The raw response content from the API.
    """
    ths_url = 'https://quantapi.51ifind.com/api/v1/edb_service'
    ths_para = {"indicators": f"{id_}",
                "startdate": f"{startdate}",
                "enddate": f"{enddate}"}
    ths_response = requests.post(url=ths_url, json=ths_para, headers=ths_headers)
    return ths_response.content


def get_data(startdate, enddate):
    """
    Retrieves data for a list of IDs from the EDB service and returns a list of DataFrames.

    Args:
        startdate (str): The start date for the data (format: 'YYYY-MM-DD').
        enddate (str): The end date for the data (format: 'YYYY-MM-DD').

    Returns:
        list: A list of pandas DataFrames, each containing time series data for an indicator.
    """
    df_list = []
    for id_ in id_list:
        response = edb(id_, startdate, enddate)
        response = json.loads(response.decode('utf-8'))
        df = pd.DataFrame({'time': response['tables'][0]['time'], 'value': response['tables'][0]['value']})
        if response['tables'][0]['index_name'] != []:
            id_name = response['tables'][0]['index_name'][0]
            df = df.rename(columns={'time': 'DATE', 'value': id_name})
            df_list.append(df)
            print(id_name, '更新完成')
    return df_list


def update_data_ifind(start_date='2016-01-01', end_date=None, file_path='data/X_data_iFind.csv'):
    """
    Updates the data from the EDB service and saves it to a CSV file. The data is resampled monthly.

    Args:
        start_date (str): The start date for the data (format: 'YYYY-MM-DD').
        end_date (str): The end date for the data (format: 'YYYY-MM-DD'). Defaults to the current date.
        file_path (str): The path to the CSV file where the updated data will be saved.
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    df_list = get_data(start_date, end_date)
    df = pd.concat(df_list)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    df.sort_index()
    df_resampled = df.resample('ME').last()
    df_resampled.to_csv(file_path, encoding='gbk')


if __name__ == '__main__':
    update_data_ifind()
    print('Ifind数据更新完成')
