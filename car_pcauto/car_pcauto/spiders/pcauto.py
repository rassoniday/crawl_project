# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from xpathrule import XpathRule
from ..items import CarPcautoItem
from bs4 import BeautifulSoup
import re
from bs4 import BeautifulSoup
class PcautoSpider(Spider):

    flag = True
    name = "pcauto"
    item = CarPcautoItem()
    start_urls = [
        'http://www.pcauto.com.cn/nation/gckx/ ',
        'http://www.pcauto.com.cn/nation/gwkx/ ',
        'http://www.pcauto.com.cn/nation/ycxc/ ',
        'http://www.pcauto.com.cn/nation/dz/ ',
        #
        'http://www.pcauto.com.cn/teach/bijiao/ ',
        'http://www.pcauto.com.cn/teach/xcdg/ ',
        'http://www.pcauto.com.cn/teach/tiyan/ ',
        'http://www.pcauto.com.cn/teach/tuijian/ ',
        #
        'http://www.pcauto.com.cn/tech/kuaixun/ ',
        'http://www.pcauto.com.cn//tech/xuetang/ ',
        'http://www.pcauto.com.cn/tech/pz/ ',
        'http://www.pcauto.com.cn/tech/fx/ ',

        "http://www.pcauto.com.cn/drivers/yangche/point/ ",
        'http://www.pcauto.com.cn/drivers/yangche/bysc/ ',
        'http://www.pcauto.com.cn/drivers/yangche/falvfagui/ ',
        'http://www.pcauto.com.cn/drivers/yangche/sgbx/ ',

        'http://www.pcauto.com.cn/drivers/tire/ltdg/ '
        'http://drivers.pcauto.com.cn/tire/ltty/ ',
        'http://drivers.pcauto.com.cn/tire/ltpc/ ',
        'http://drivers.pcauto.com.cn/tire/syjq/ '
        'http://drivers.pcauto.com.cn/tire/xpkx/ ',
        #
        'http://www.pcauto.com.cn/drivers/machineoil/jysyjq/ ',
        'http://www.pcauto.com.cn/drivers/machineoil/jydthwqb/ ',
        'http://www.pcauto.com.cn/news/hyxw/ ',
        'http://www.pcauto.com.cn/news/gjdt/ ',
        'http://www.pcauto.com.cn/news/ft/ ',
        'http://www.pcauto.com.cn/news/changshang/ ',

        'http://www.pcauto.com.cn/wenhua/jingdian/ ',
        'http://www.pcauto.com.cn/wenhua/pinpai/ ',
        'http://www.pcauto.com.cn/wenhua/cehua/ ',

        'http://www.pcauto.com.cn/pingce/tiyan/ ',
        'http://www.pcauto.com.cn/pingce/yc/ ',
        'http://www.pcauto.com.cn/pingce/dbpc/ ',
        'http://www.pcauto.com.cn/pingce/cqcs/'

    ]

    def start_requests(self):
        # print self.start_urls
        _MAXPAGE_ = 2
        for urlitem in self.start_urls:
            # print urlitem
            yield Request(url = urlitem.strip(), callback=self.parse)
            n = 1
            self.flag = True
            while n < _MAXPAGE_ and self.flag:

                yield Request(url=urlitem.replace('/ ', '/index_{}.html').format(n), callback=self.parse)
                n += 1


    def parse(self, response):
        urllist = response.xpath(XpathRule.url).extract()
        if urllist:
            for urlitem in urllist:
                yield Request(url=urlitem, callback=self.detailparse)
        else:
            self.flag = False

    def detailparse(self, response):

        self.item['url'] = response.url
        self.item['title'] = response.xpath(XpathRule.title).extract()[0].strip() if response.xpath(XpathRule.title).extract() else None
        self.item['content'] = str(BeautifulSoup(response.body, 'html5lib').find('div', attrs={'class':'artText clearfix'})).replace('#src','temp').replace('src','#src').replace('temp','src')

        # self.item['content'] = str(self.item['content']).replace('#src','temp').replace('src','gifsrc').replace('temp','src')
        # print(type(self.item['content']))
        # print self.item['content']
        # self.item['content'] = BeautifulSoup(response.body, 'html5lib').find('div', attrs={'class': 'artText clearfix'})
        # gif_img = 'src="http://img0.pcauto.com.cn/pcauto/1309/13/3059862_blank.gif" '
        # # self.item['content'] = str(self.item['content']).replace(gif_img,'').replace('#','')
        # # print self.item['content']
        # # print '*'*10
        # giflist= re.findall('http://img0.pcauto.com.cn/pcauto/1309/13/3059862_blank.gif',response.body)
        # imglist = re.findall('blank.gif" #src="(.*?)" ', response.body)
        # for i in range(0,len(giflist)):
        #     giflist[i]=giflist[i]+str(i)
        #     self.item['content']=self.item['content'].sub(imglist[i],gif_img, count=1)
        # print self.item['content']
        #     # giflist[i]=imglist[i]
        #     # print giflist[i]
        #
        # print imglist
        # print len(imglist)
        # print giflist
        #
        self.item['column'] = ''.join(response.xpath(XpathRule.column).extract()) or None
        self.item['labels'] = ' '.join(set(response.xpath(XpathRule.labels).extract()))
        self.item['abstract'] = None
        # print re.findall('blank.gif" #src="(.*?)" ',response.body)
        self.item['imgurl'] = " ".join(re.findall('blank.gif" #src="(.*?)" ',response.body))
        self.item['publishtime'] = response.xpath(XpathRule.publishtime).extract()[0].strip() + ":00"
        self.item['source'] = response.xpath(XpathRule.source).extract()[0]#.replace("来源：","").strip()
        self.item['author'] = ''.join(response.xpath(XpathRule.author).extract()).replace(u"作者：","") or None
        # print self.item['content']
        # print self.item
        yield self.item