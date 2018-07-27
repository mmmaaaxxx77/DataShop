import json
from asyncio import sleep

import requests
from bs4 import BeautifulSoup

from crawler.mongo.model import CollectorCount
import traceback

from logger import logconf

logger = logconf.Logger(__name__)


def get_url_stock_list(url, type="get", pdata={}):
    if type == 'get':
        ret = requests.get(url)
    else:
        ret = requests.post(url, data=pdata)

    bu = BeautifulSoup(ret.text, 'html.parser')
    list = bu.select("tr")

    result_list = []
    for sub in list:
        result_list.append([i.text.strip() for i in sub.select("td")])
        # print([i.text.strip() for i in sub.select("td")])

    return result_list[1:]


def get_dates(num=5):
    url = "http://www.tdcc.com.tw/smWeb/QryStockAjax.do"
    pdata = {
        'REQ_OPR': "qrySelScaDates",
    }
    ret = requests.post(url, data=pdata)

    if "timed out" in ret.text:
        return get_dates()

    result = json.loads(ret.text)[:num]
    result.reverse()
    return result


def get_stock_data(stock_id=1240, date=20180720, from_n=0):
    url = "http://www.tdcc.com.tw/smWeb/QryStockAjax.do"
    pdata = {
        'scaDates': date,
        'scaDate': date,
        'SqlMethod': 'StockNo',
        'StockNo': stock_id,
        'radioStockNo': stock_id,
        'clkStockNo': stock_id,
        'REQ_OPR': 'SELECT',
    }

    ret = requests.post(url, data=pdata)

    if "timed out" in ret.text:
        return get_stock_data(stock_id, date, from_n)

    bu = BeautifulSoup(ret.text, 'html.parser')
    all_td = bu.select("table.mt")[1].select("tr")
    all_td = all_td[1:-1]
    format_data = []
    for d in all_td:
        td = d.select("td")

        format_data.append([
            td[0].text,
            td[1].text,
            td[2].text,
            td[3].text,
            td[4].text,
        ])

    return format_data[from_n:]


def do_count_stock(stock_id='2317', stock_name="鴻海", stock_type="上市"):
    five_dates = get_dates()
    stock_data_lists = {}

    date_count = {}

    def _count(value, next_list):
        return value + int(next_list[2].replace(",", ""))

    for date in five_dates:
        sd = get_stock_data(int(stock_id), int(date))
        stock_data_lists[date] = sd

        # count
        total_count = 0  # 9項-15項
        # print(sd)
        for ss in sd[8:15]:
            total_count = _count(total_count, ss)
        date_count[date] = total_count

    five_dates.reverse()

    result = []
    for ind in range(0, len(five_dates) - 1):
        ddate = five_dates[ind]
        ddate_count = date_count[ddate]

        last_count = date_count[five_dates[ind + 1]]
        d = {
            'stock_id': stock_id,
            'stock_name': stock_name,
            'stock_type': stock_type,
            'date': ddate,
            'count': ddate_count,
            'difference_count': ddate_count - last_count,
            'data': stock_data_lists[ddate]
        }
        result.append(d)

        CollectorCount.objects(stock_id=stock_id, data_date=ddate).delete()

        try:
            model = CollectorCount(stock_id=stock_id,
                                   stock_name=stock_name,
                                   stock_type=stock_type,
                                   data_date=ddate,
                                   data_count=ddate_count,
                                   data_difference_count=ddate_count - last_count,
                                   data_data=stock_data_lists[ddate])
            model.save()
        except Exception as e:
            logger.error(f"{stock_id} {stock_name}")
            logger.error(e)
        logger.info(d)


def auto_maintain():
    def _do_work(url, type):
        # get stock list
        stock_list = get_url_stock_list(url)

        for stock in stock_list:
            stock_name = stock[3]
            stock_id = stock[2]
            logger.info(f"{stock_id} {stock_name}")
            do_count_stock(stock_id, stock_name, type)
            sleep(2)

    # 上市
    logger.info("---上市---")
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=1&"
           "issuetype=1&industry_code=&Page=1&chklike=Y")
    _do_work(url, "上市")
    sleep(10)

    logger.info("---上櫃---")
    # 上櫃
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=2&"
           "issuetype=4&industry_code=&Page=1&chklike=Y")
    _do_work(url, "上櫃")
    sleep(10)

    logger.info("---興櫃---")
    # 興櫃
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=4&"
           "issuetype=R&industry_code=&Page=1&chklike=Y")
    _do_work(url, "興櫃")
    sleep(10)

    logger.info("---- ALL DONE ----")

    sleep(60 * 60 * 24 * 2)


if __name__ == '__main__':
    # print(get_dates())
    # print(get_stock_data())
    #do_count_stock('2883')
    auto_maintain()
