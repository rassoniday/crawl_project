# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class DzdpFoodItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cdb = Field()
    cuisine = Field()
    restaurant = Field()
    address = Field()
    phone = Field()
    score = Field()
    cm_num = Field()
    cm_attribute = Field()
    foods = Field()
    dt = Field()
    source = Field()
    group_id = Field()
    url = Field()
    district =Field()
    CBD =Field()
    city = Field()
    cm_author =Field()
    cm_content = Field()
    cm_zan = Field()
    cm_response  = Field()
    cm_collect = Field()
    cm_inform = Field()
    cm_pub_time = Field()
