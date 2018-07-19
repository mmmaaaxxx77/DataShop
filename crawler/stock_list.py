import datetime
from time import sleep
import xlsxwriter
import re
import traceback

import requests
from bs4 import BeautifulSoup
from mongoengine import connect

from mongo.model import Stock, ShareHolder

from logger import logconf

logger = logconf.Logger(__name__)


def get_url_stock_total(stock_id):
    url = "http://mops.twse.com.tw/mops/web/t05st03"
    pdata = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'co_id': stock_id,
    }

    ret = requests.post(url, data=pdata)
    ret.encoding = 'utf8'

    bu = BeautifulSoup(ret.text, 'html.parser')

    all_td = bu.select("#table01 > table")[1].select("td")
    total = ''
    for a in all_td:
        if '(含私募' in a.text:
            total = a.text
            break
    total = total.strip().replace(",", "").replace("\n", "").replace(" ", "")
    total = re.sub(r'\(含私募\d*股\)', "", total)

    total = total.replace("\n", "").replace(",", "").replace("股", "")
    return int(total)


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


def get_stock_director(stock_id):
    url = f"http://just2.entrust.com.tw/z/zc/zck/zck_{stock_id}.djhtm"

    ret = requests.get(url)
    # ret.encoding = 'utf8'

    bu = BeautifulSoup(ret.text, 'html.parser')
    logger.info(stock_id)
    list = bu.select("table.t01")[0].select("tr")[2:-1]

    result_list = []

    def _data_clear(tds):
        rs = []
        rs.append(tds[0].text.strip())
        rs.append(tds[1].text.strip())
        rs.append(tds[2].text.strip().replace(",", ""))
        rs.append(tds[3].text.strip())
        return rs

    for d in list:
        result_list.append(_data_clear(d.select("td")))

    update_date = bu.select("div.t11")[0].text.strip().replace("資料日期:", "").replace("/", "")

    return int(update_date), result_list


def get_stock_director03(stock_id):
    url = f"https://sjmain.esunsec.com.tw/z/zu/zub/zubf/zubfa/zubfa_ASR{stock_id}.djhtm"

    ret = requests.get(url)
    # ret.encoding = 'utf8'

    bu = BeautifulSoup(ret.text, 'html.parser')
    logger.info(stock_id)
    _list = bu.select("table.zuTable2")[0].select("tr")[2:]

    list = []
    for lis in _list:
        if '＊來自' in lis.text:
            break
        else:
            list.append(lis)

    result_list = []

    def _data_clear(tds):
        rs = []
        rs.append(tds[0].text.strip())
        rs.append(tds[1].text.strip())
        rs.append(tds[2].text.strip().replace(",", ""))
        rs.append(tds[3].text.strip())
        return rs

    for d in list:
        result_list.append(_data_clear(d.select("td")))

    update_date = bu.select("div.zuHead1-10R")[0].text.strip()[:11].replace("資料日期:", "").replace("/", "")

    return int(update_date), result_list


def write_excel(stock_name, stock_id, path):
    update_date, data = get_stock_director(stock_id)
    workbook = xlsxwriter.Workbook(f'{path}/{stock_id}_{stock_name}_{update_date}.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, '職稱')
    worksheet.write(0, 1, '姓名/法人名稱')
    worksheet.write(0, 2, '持股張數')
    worksheet.write(0, 3, '持股比例')

    data = get_stock_director(stock_id)[1]

    for indx in range(0, len(data)):
        d = data[indx]
        _indx = indx + 1
        worksheet.write(_indx, 0, d[0])
        worksheet.write(_indx, 1, d[1])
        worksheet.write(_indx, 2, d[2])
        worksheet.write(_indx, 3, d[3])

    workbook.close()


def auto_maintain():

    def _write_director_to_mongo(stock_name, stock_id, type, update_date, data):

        for d in data:
            _data = {
                'type': type,
                'stock_id': stock_id,
                'stock_name': stock_name,
                'stock_update_date': update_date,
                'stock_type': type,
                'create_date': datetime.datetime.now(),
                'shareholder_position': d[0],
                'shareholder_name': d[1],
                'shareholder_stock_count': d[2],
                'shareholder_stock_percentage': d[3],
            }
            logger.info(_data)
            # write to mongo
            _model = ShareHolder(stock_id=stock_id,
                                 stock_name=stock_name,
                                 stock_type=type,
                                 position=d[0],
                                 name=d[1],
                                 stock_count=d[2],
                                 stock_percentage=d[3] if '%' in d[3] else f'{d[3]}%',
                                 stock_update_date=str(update_date))
            _model.save()

    def _do_work(url, type):

        # get stock list
        stock_list = get_url_stock_list(url)

        # write to mongo
        Stock.objects(stock_type=type).delete()
        logger.info("清除所有Stock資料")
        for d in stock_list:
            print(f"{d[2]} {d[3]}")
            _data = Stock(stock_id=d[2], stock_name=d[3], stock_type=type)
            _data.save()

        # format all data
        for index in range(0, len(stock_list)):
            stock = stock_list[index]
            stock_name, stock_id = stock[3], stock[2]
            update_date, data = get_stock_director(stock_id)

            logger.info(f"清除所有 {stock_name} {stock_id} 資料")
            ShareHolder.objects(stock_id=stock_id).delete()

            logger.info(f"開始寫入 {stock_name} {stock_id} 資料")
            _write_director_to_mongo(stock_name, stock_id, type, update_date, data)

            sleep(10)

    def _do_work_only_03_stock(url, type):

        # get stock list
        stock_list = get_url_stock_list(url)

        # write to mongo
        Stock.objects(stock_type=type).delete()
        logger.info("清除所有Stock資料")
        for d in stock_list:
            print(f"{d[2]} {d[3]}")
            _data = Stock(stock_id=d[2], stock_name=d[3], stock_type=type)
            _data.save()

        # format all data
        for index in range(0, len(stock_list)):
            stock = stock_list[index]
            stock_name, stock_id = stock[3], stock[2]
            update_date, data = get_stock_director03(stock_id)

            logger.info(f"清除所有 {stock_name} {stock_id} 資料")
            ShareHolder.objects(stock_id=stock_id).delete()

            logger.info(f"開始寫入 {stock_name} {stock_id} 資料")
            _write_director_to_mongo(stock_name, stock_id, type, update_date, data)

            sleep(10)


    # 上市
    logger.info("---上市---")
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=1&"
           "issuetype=1&industry_code=&Page=1&chklike=Y")
    try:
        _do_work(url, "上市")
    except Exception as e:
        logger.error(traceback.print_stack())

    sleep(10)

    logger.info("---上櫃---")
    # 上櫃
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=2&"
           "issuetype=4&industry_code=&Page=1&chklike=Y")
    try:
        _do_work(url, "上櫃")
    except Exception as e:
        logger.error(traceback.print_stack())
    sleep(10)

    logger.info("---興櫃---")
    # 興櫃
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=4&"
           "issuetype=R&industry_code=&Page=1&chklike=Y")
    try:
        _do_work_only_03_stock(url, "興櫃")
    except Exception as e:
        logger.error(traceback.print_stack())
    sleep(10)

    logger.info("---- ALL DONE ----")

    sleep(60 * 60 * 24 * 2)


if __name__ == '__main__':

    auto_maintain()
    #print(get_stock_director03(1240))

    # print(get_url_stock_total(1264))
    # print(get_url_stock_total(1258))

    # print(get_stock_result(1108))

    #write_excel("潤泰全", 2915, "上市")


    # print(get_stock_director(1108))


    def _do(url, type):
        data = get_url_stock_list(url)

        print(data)

        for ind in range(0, len(data)):
            d = data[ind]
            write_excel(d[3], d[2], type)
            print(f"{ind}/{len(data)}")
            sleep(5)

            # 上市
            # url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
            #        "owncode=&stockname=&isincode=&market=1&"
            #        "issuetype=1&industry_code=&Page=1&chklike=Y")
            #
            # _do(url, "上市")
            # sleep(10)

            # print("------")
            # 上櫃
            # url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
            #        "owncode=&stockname=&isincode=&market=2&"
            #        "issuetype=4&industry_code=&Page=1&chklike=Y")
            # _do(url, "上櫃")
            # sleep(10)
            #
            # print("------")
            # # 興櫃
            # url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
            #        "owncode=&stockname=&isincode=&market=4&"
            #        "issuetype=R&industry_code=&Page=1&chklike=Y")
            # _do(url, "興櫃")
            # sleep(10)
            #
            # print("------")
            # # 創櫃
            # url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
            #        "owncode=&stockname=&isincode=&market=A&"
            #        "issuetype=C&industry_code=&Page=1&chklike=Y")
            # get_url_stock_list(url)
            # sleep(10)
