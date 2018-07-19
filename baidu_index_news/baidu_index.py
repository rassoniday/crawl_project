# -*- coding:utf-8 -*-

import os
import re
import time
import requests
from lxml import etree
from database import Database

cookie_text = 'BAIDUID=4AE23A509F707BAFBC47958E5C43BFAA:FG=1; ' \
              'BIDUPSID=4AE23A509F707BAFBC47958E5C43BFAA; ' \
              'PSTM=1499231599; BD_CK_SAM=1; PSINO=2; BD_HOME=0; ' \
              'H_PS_PSSID=22952_1461_21099_18559_17001_23632; BD_UPN=123253; ' \
              'H_WISE_SIDS=102569_104496_117034_117159_104885_100098_117020' \
              '_117419_116918_107319_116765_117276_117584_117332_117237_117456_117430_' \
              '116995_117171_116309_115532_116689_117562_117553_115350_117517_117175_' \
              '116412_116523_110085_114571_117027; BDSVRTM=34; plus_lsv=c924113c2f1a29b1; ' \
              'plus_cv=1::m:13b3db50; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1499236788; ' \
              'Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1499236788; BDORZ=AE84CDB3A529C0F8A2B9DCDD1D18B695'

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36'}


def get_index_news():
    BDSVRTM = get_BDSVRTM()
    cookies = format_cookie(cookie_text)
    if BDSVRTM:
        cookies['BDSVRTM'] = BDSVRTM
    res = requests.get(url="https://www.baidu.com/", timeout=10, headers=headers, cookies=cookies)
    save_BDSVRTM(res)
    return res.text


def get_links():
    html = etree.HTML(get_index_news())
    links = html.xpath("//div[@class='news-list-wrapper']//a/@href")
    return links


def parser_news():
    db = db_init()
    for link in get_links():
        try:
            res = get_news_res(link)
            news_html = etree.HTML(res.text)
            title = news_html.xpath("//title/text()")[0]
            source = news_html.xpath("//span[@class='info-src']/text()")
            createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            p_time = re.search(r'(?<=pvTime: ")[^"]*', res.text)
            publishtime = p_time.group() if p_time else createtime
            content = etree.tostring(news_html.xpath('//div[@class="article-body"]')[0])
            labels = '|'.join(news_html.xpath("//div[@class='article-label hide']//span/text()"))
            data = [title, source, publishtime, content, labels, res.url, createtime]
            print data
            insert_db(db, data)
        except Exception:
            continue
    db.close()



def insert_db(db, data):
    in_2_db = """insert ignore into baidu_news_PhoneBrowser(title,source,publishtime,content,labels,url,create_time)
                                     value(%s, %s, %s, %s, %s, %s, %s)"""
    db.execute(in_2_db, data)


def db_init():
    db = Database()
    db.connect('crawl_data')
    return db


def get_news_res(link):
    res = requests.get(url=link, timeout=10, headers=headers)
    return res


def get_BDSVRTM():
    if not os.path.exists('./baidu_cookies.txt') or not os.path.getsize('./baidu_cookies.txt'):
        return None
    with open('./baidu_cookies.txt', 'r') as ck_stream:
        BDSVRTM = ck_stream.read()
    return BDSVRTM


def save_BDSVRTM(res):
    with open('./baidu_cookies.txt', 'w') as ck_stream:
        ck_stream.write(res.cookies['BDSVRTM'])


def format_cookie(cookies_text):
    cookies = {}
    for ck_item in cookies_text.split(';'):
        k, v = ck_item.split('=', 1)
        cookies[k] = v
    return cookies

if __name__ == "__main__":
    parser_news()