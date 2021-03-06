# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


from scrapy import Item, Field
class CarPcautoItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    abstract = Field()
    url = Field()
    publishtime = Field()
    author = Field()
    source = Field()
    content = Field()
    column = Field()
    labels = Field()
    imgurl = Field()