# -*- coding: utf-8 -*-
import re
import json
import requests
from requests import ConnectionError, ReadTimeout
from urllib import quote
from urlparse import urljoin
from ..items import DzdpFoodItem
from scrapy import Spider, Request


class Xpath:
    city_list_rule = "//div[@class='group clearfix']/a/@href"
    res_list_rule = "//div[@id='shop-all-list']/ul/li"
    res_url_rule = ".//div[@class='tit']/a[1]/@href"
    res_cuisine_rule = ".//div[@class='tag-addr']/a[1]/span/text()"
    res_cdb_rule = ".//div[@class='tag-addr']/a[2]/span/text()"
    next_page_rule = "//a[@class='next']/@href"
    res_name_rule = "//h1[@class='shop-name']/text()"
    res_adr_rule = "//span[@itemprop='street-address']/text()"
    res_tel_rule = "//p[@class='expand-info tel']/span/text()"
    res_cm_num_rule = "//span[@id='reviewCount']/text() | //div[@class='brief-info']/span[2]/text()"
    res_score_rule = "//div[@class='brief-info']/span[1]/@class"
    res_cm_attribute_rule = "//span[@id='comment_score']/span/text()"


class FoodSpider(Spider):
    name = "food"
    item = DzdpFoodItem()
    allowed_domains = ["dianping.com"]
    food_url_template = "https:{}/food"
    start_urls = ['https://www.dianping.com/']
    cuisine_headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection': 'close',
    'Host': 'www.dianping.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko)' \
                  ' Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}

    def parse(self, response):
        city_urls = response.xpath(Xpath.city_list_rule).extract()
        for url in city_urls:
            yield Request(url=self.food_url_template.format(url),
                          callback=self.parse_food_detail)

    def parse_food_detail(self, response):
        food_categorys = re.findall(r'/search/category/\d+/\d+/[^"]+', response.body)
        for category in food_categorys:
            yield Request(url=urljoin("http://www.dianping.com", category),
                          callback=self.parse_res_list)

    def parse_res_list(self, response):
        res_list = response.xpath(Xpath.res_list_rule)
        for restaurant in res_list:
            res_url = restaurant.xpath(Xpath.res_url_rule).extract()[0]
            yield Request(url=urljoin("http://www.dianping.com", res_url),
                          meta={'cuisine': restaurant.xpath(Xpath.res_cuisine_rule).extract()[0],
                                'cdb': restaurant.xpath(Xpath.res_cdb_rule).extract()},
                          callback=self.parse_res_detail)
        next_url = response.xpath(Xpath.next_page_rule).extract()
        if next_url:
            yield Request(url=urljoin("http://www.dianping.com", next_url[0]),
                          callback=self.parse_res_list)

    def parse_res_detail(self, response):
        self.item['restaurant'] = response.xpath(Xpath.res_name_rule).extract()[0].strip()
        self.item['address'] = response.xpath(Xpath.res_adr_rule).extract()[0].strip()
        self.item['phone'] = ' '.join(response.xpath(Xpath.res_tel_rule).extract())
        self.item['score'] = int(response.xpath(Xpath.res_score_rule).re(r'\d+')[0]) * 0.1
        self.item['cm_num'] = response.xpath(Xpath.res_cm_num_rule).extract()[0]
        self.item['cm_attribute'] = ','.join(response.xpath(Xpath.res_cm_attribute_rule).extract())
        self.item['cuisine'] = response.meta['cuisine']
        self.item['cdb'] = response.meta['cdb'][0] if response.meta['cdb'] else None
        self.item['foods'] = self.get_cuisine(response)
        self.item['url'] = response.url

        yield self.item

    def get_cuisine(self, response):
        try:
            shopId = re.search(r'(?<=shopId: )\d+', response.body).group()
            cityId = re.search(r'(?<=cityId: )\d+', response.body).group()
            shopName = re.search(r'(?<=shopName: ")[^"]+', response.body).group()
            power = re.search(r'(?<=power: )\d+', response.body).group()
            shopType = re.search(r'(?<=shopType:)\d+', response.body).group()
            mainCategoryId = re.search(r'(?<=mainCategoryId:)\d+', response.body).group()
        except AttributeError:
            return None
        self.cuisine_headers['referer'] = response.url
        cuisine_template = "http://www.dianping.com/ajax/json/shopDynamic/shopTabs?shopId={}&cityId={}&shopName={}" \
                           "&power={}&mainCategoryId={}&shopType={}&shopCityId={}"
        for i in xrange(0,5):
            try:
                proxy = self.get_proxy()
                proxies = {
                    "http": "http://%s:%s" % (proxy['ip'], proxy['port']),
                    "https": "https://%s:%s" % (proxy['ip'], proxy['port'])
                }
                res = requests.get(url=cuisine_template.format(shopId, cityId, quote(shopName), power,
                                                               mainCategoryId, shopType, cityId),
                                   headers=self.cuisine_headers,
                                   proxies=proxies,
                                   timeout=10)
                break
            except (ConnectionError, ReadTimeout) as errinfo:
                print 'errinfo', errinfo
                continue
        return ','.join([cuisine['dishTagName'] for cuisine in json.loads(res.text)['allDishes']])


    def get_proxy(self):
        res = requests.get(url='http://139.162.99.142:5000',
                           auth=('icaruslou', 'f3d9c92b3ea1959ddb0f5140eb5caaec')).text
        proxy = res.split(':')
        return {'ip': proxy[0], 'port': proxy[1]}

