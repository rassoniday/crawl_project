# -*- coding: utf-8 -*-
import time
from database import Database
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DzdpFoodPipeline(object):

    data_to_res = "insert ignore into mds_crw_dianping_restaurant(cdb, cuisine, restaurant, address, " \
                  "phone, score, cm_num, cm_attribute, foods, dt, shop_url)value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_to_cui = "insert ignore into mds_crw_dianping_food(food, dt)value(%s,%s)"
    data_to_shangqu = "insert ignore into crawl_data.mds_crw_dianping_CBD(city, district, CBD, dt, source, group_id)value(%s,%s,%s,%s,%s,%s)"
    data_to_food_comment ="insert ignore into crawl_data.mds_crw_dianping_restaurant_koubei(restaurant, cm_author, score, cm_attribute, cm_pub_time," \
                          "cm_content, cm_zan, cm_response, cm_collect, cm_inform, url, dt, group_id, source)value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    def open_spider(self, spider):
        self.db = Database()
        self.db.connect('crawl_data')

    def process_item(self, item, spider):
        try:
            if spider.name in ['shangqu']:
                print '------------------------------database,run'
                shangqu_data = [item['city'], item['district'], item['CBD'], item['dt'],
                                      item['source'], item['group_id']]
                self.db.execute(self.data_to_shangqu, shangqu_data)
                print '------------------------------database,end'
            if spider.name in ['food_comment']:
                print '------------------------------database,run'
                food_comment_data = [item['restaurant'],item['cm_author'],item['score'],item['cm_attribute'],
                                     item['cm_pub_time'],item['cm_content'],item['cm_zan'],item['cm_response'],
                                     item['cm_collect'],item['cm_inform'],item['url'],item['dt'],item['group_id'],item['source']]
                self.db.execute(self.data_to_food_comment,food_comment_data)
                print '------------------------------database,end'
            if spider.name in ['food*']:
                res_data = [item['cdb'], item['cuisine'], item['restaurant'], item['address'],
                            item['phone'], item['score'], item['cm_num'], item['cm_attribute'],
                            item['foods'], time.strftime("%Y%m%d"), item['url']]
                self.db.execute(self.data_to_res, res_data)
                if item['foods']:
                    for food in item['foods'].split(','):
                        try:
                            self.db.execute(self.data_to_cui, [food, time.strftime("%Y%m%d")])
                        except Exception:
                            continue
                return item

        except Exception as errinfo:
            return item

    def close_spider(self, spider):
        self.db.close()