# -*- coding: utf-8 -*-
# @Time    : 2019/11/12 9:50
# @Author  : Yasaka.Yu
# @File    : __init__.py.py
import random


markets = [
    {'LatestUrl': 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1800_jgxxgk&TABKEY=tab1&PAGENO=1&selectBkmc=0&random={}'.format(random.random()),
     'MarketType': 1, 'Column': "监管措施"},
    {'LatestUrl': 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1800_jgxxgk&TABKEY=tab2&PAGENO=1&selectGsbk=0&random={}'.format(random.random()),
     'MarketType': 2, 'Column': "纪律处分"},
]


def get_url():
    for data in markets:
        url = data.get('LatestUrl')
        yield url


if __name__ == '__main__':
    results = get_url()
    for result in results:
        print(result)