# -*- coding: utf-8 -*-

import json
import pymysql
import requests

api = ''



database = pymysql.connect(
                           host='',
                           port=3306,
                           user='',
                           password='',
                           db='th_spider_database',
                           charset='utf8',
                           )
cursor = database.cursor()

sql = "select * from th_spider_database.data_set where circleKey='%s' order by noteDate desc limit 50;"
circleKeys = [
    'TH001',
    'TH002',
    'TH003',
    'TH004',
    'TH005',
    'TH006',
    'TH007',
    'TH008',
    'TH009',
    'TH010',
    'TH011',
    'TH012',
    'TH013',
    'TH014',
    'TH015',
    'TH016',
    'XQ002',


]

headers = {'Content-Type': 'application/json'}

for key in circleKeys:
    temp_sql = sql%key
    cursor.execute(temp_sql)
    data_list = cursor.fetchall()

    for data in data_list:
        apiData = {
            'id': data[0],
            'title': data[1],
            'noteDate': data[2],
            'htmlContent': data[3],
            'tags': data[4],
            'circleKey': data[5],
            'coverPic': data[6],
            'coverPicType': data[7],
            'src': data[8]
        }
        print(apiData)
        json_str = json.dumps(apiData)
        response = requests.post(url=api, data=json_str, headers=headers)
        print(response.text)