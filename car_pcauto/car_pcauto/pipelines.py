# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import traceback
from database import Database

class CarPcautoPipeline(object):
    insertsql = """insert ignore into car_pcauto(title, abstract, url, publishtime, author, content, imgurl, newscolumn, source, labels, category)
                                           value(%s, %s, %s, %s, %s ,%s, %s, %s, %s, %s, DEFAULT)"""

    def open_spider(self, spider):
        self.database = Database()
        self.database.connect('crawl_data')

    def process_item(self, item, spider):
        try:
            insertdata = (
                item['title'], item['abstract'], item['url'],
                item['publishtime'], item['author'], item['content'],
                item['imgurl'], item['column'], item['source'], item['labels']
            )

            self.database.execute(self.insertsql, insertdata)
        except Exception as errinfo:
            print errinfo
            traceback.print_exc()
        return item

    def close_spider(self, spider):
        self.database.close()