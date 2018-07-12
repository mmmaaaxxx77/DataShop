from time import sleep
import xlsxwriter
import re

import requests
from bs4 import BeautifulSoup


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
    # list = bu.select("#table01 > table:nth-child(3) > tr:nth-child(9) > td:nth-child(2)")
    # total = bu.select("#table01 > table")[1].select("tr")[11].select("td")[0].text.strip()

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


def get_url_stock_total2(stock_id):
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
    # list = bu.select("#table01 > table:nth-child(3) > tr:nth-child(9) > td:nth-child(2)")
    total = bu.select("#table01 > table")[1].select("tr")[14].select("td")[0].text.strip()
    total = total.replace("\n", "").replace(",", "").replace("(含私募                  0股)", "").replace("股", "")
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
    url = "http://mops.twse.com.tw/mops/web/ajax_stapap1"
    pdata = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'true',
        'co_id': stock_id,
    }

    ret = requests.post(url, data=pdata)
    ret.encoding = 'utf8'

    bu = BeautifulSoup(ret.text, 'html.parser')
    list = bu.select("table.hasBorder > tr")

    result_list = []

    def _clear_data(line):
        line[2] = int(line[2].replace(",", ""))
        line[3] = int(line[3].replace(",", ""))
        line[4] = int(line[4].replace(",", ""))

        return line

    for sub in list:
        if (sub.select('td')[0].text.strip() != "職稱" and
                    sub.select('td')[0].text.strip() != "內部人關係人目前持股合計"):
            result_list.append(_clear_data([i.text.strip() for i in sub.select('td')]))
            # print([i.text.strip() for i in sub.select('td')])

    update_date = bu.select("td.reportCont")[0]
    # print(update_date.text.strip())

    return int(update_date.text.strip()[5:]), result_list


def get_stock_result(stock_id):
    try:
        stock_total = get_url_stock_total(stock_id)
    except Exception as e:
        print(e)
        print(stock_id)
        stock_total = get_url_stock_total2(stock_id)

    stock_directors = get_stock_director(stock_id)[1]

    result = []

    for d in stock_directors:
        _res_d = d[:4]
        _res_d.append(round((_res_d[3] / stock_total) * 100, 2))
        result.append(_res_d)

    return result


def write_excel(stock_name, stock_id, path):
    update_date, data = get_stock_director(stock_id)
    workbook = xlsxwriter.Workbook(f'{path}/{stock_id}_{stock_name}_{update_date}.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, '職稱')
    worksheet.write(0, 1, '姓名')
    worksheet.write(0, 2, '持有股數(股)')
    worksheet.write(0, 3, '持股比例(%)')

    data = get_stock_result(stock_id)

    for indx in range(0, len(data)):
        d = data[indx]
        _indx = indx + 1
        worksheet.write(_indx, 0, d[0])
        worksheet.write(_indx, 1, d[1])
        worksheet.write(_indx, 2, d[2])
        worksheet.write(_indx, 3, d[4])

    workbook.close()


if __name__ == '__main__':
    # print(get_url_stock_total(1264))
    # print(get_url_stock_total(1258))

    # print(get_stock_result(1108))

    # write_excel("幸福", 1108, "test_data")

    # print(get_stock_director(1108))

    def _do(url, type):
        data = get_url_stock_list(url)

        print(data)

        for ind in range(0, len(data)):
            d = data[ind]
            write_excel(d[3], d[2], type)
            print(f"{ind}/{len(data)}")
            sleep(5)


    # # 上市
    # url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
    #        "owncode=&stockname=&isincode=&market=1&"
    #        "issuetype=1&industry_code=&Page=1&chklike=Y")
    #
    # _do(url, "上市")
    # sleep(10)

    print("------")
    # 上櫃
    url = ("http://isin.twse.com.tw/isin/class_main.jsp?"
           "owncode=&stockname=&isincode=&market=2&"
           "issuetype=4&industry_code=&Page=1&chklike=Y")
    _do(url, "上櫃")
    sleep(10)
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
