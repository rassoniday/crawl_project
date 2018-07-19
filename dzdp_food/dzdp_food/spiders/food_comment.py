# -*- coding: utf-8 -*-
import re
import json
import requests
from requests import ConnectionError, ReadTimeout
from urllib import quote
from urlparse import urljoin
from ..items import DzdpFoodItem
from scrapy import Spider, Request
import datetime


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
    name = "food_comment"
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
            url = 'http://www.dianping.com{}/review_more'.format(res_url)
            yield Request(url=url,
                          meta={'cuisine': restaurant.xpath(Xpath.res_cuisine_rule).extract()[0],
                                'cdb': restaurant.xpath(Xpath.res_cdb_rule).extract()},
                          callback=self.parse_res_detail)
        next_url = response.xpath(Xpath.next_page_rule).extract()
        if next_url:
            url = 'http://www.dianping.com{}/review_more'.format(next_url[0])
            yield Request(url=url,
                          callback=self.parse_res_list)

    def parse_res_detail(self, response):
        self.item['restaurant'] = response.xpath('//h1/a/text()').extract()[0].strip()
        comment_contentlist = response.xpath('//div[@class="comment-list"]/ul/li')
        for comment_content in comment_contentlist:
            self.item['cm_author'] = comment_content.xpath('.//p[@class="name"]/a/text()').extract()[0]
            self.item['score'] = int(comment_content.xpath('.//div[@class="user-info"]/span/@class').re(r'\d+')[0]) * 0.1
            self.item['cm_attribute'] = ','.join(comment_content.xpath('.//div[@class="comment-rst"]/span[@class="rst"]/text()').extract())
            self.item['cm_pub_time'] = comment_content.xpath('.//span[@class="time"]/text()').extract()[0].strip()
            data = comment_content.xpath('.//div[@class="J_brief-cont"]')
            self.item['cm_content'] = data.xpath('string(.)').extract()[0].strip()
            self.item['cm_zan'] = comment_content.xpath('.//span[@class="countWrapper"]/a/@data-count').extract()[0] if comment_content.xpath('.//span[@class="countWrapper"]/a/@data-count').extract() else '0'
            self.item['cm_response'] = comment_content.xpath('.//span[@class="col-right"]/span[2]/a/@total').extract()[0] if comment_content.xpath('.//span[2]/a/@total').extract() else '0'
            self.item['cm_collect'] = '0'
            self.item['cm_inform'] = '0'
            self.item['url'] = response.url
            self.item['dt'] = datetime.datetime.now().strftime('%Y%m%d')
            self.item['group_id'] = '305'
            self.item['source'] = 'dianping'
            # print self.item['cm_content']
            # print response.url

            yield self.item

        next_url = response.xpath('//div[@class="comment-mode"]/div[@class="Pages"]/div[@class="Pages"]/a[@class="NextPage"]/@href').extract()
        if next_url:
            yield Request(url=urljoin(response.url, next_url[0]),
                          callback=self.parse_res_detail)

