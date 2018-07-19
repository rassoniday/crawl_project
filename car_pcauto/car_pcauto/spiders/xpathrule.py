
class XpathRule(object):
    url = "//div[@class='box-bd']//p[@class='tit blue']/a/@href"
    title = "//h1[@class='artTit']/text()"
    publishtime = "//span[@class='pubTime']/text()"
    source = "//span[@id='source_baidu']/a/text()"
    author = "//span[@class='editor']/a/text() | //span[@class='editor']/text()"
    content = "//div[@class='artText clearfix']"
    labels = "//p[@class='moreRead artTag']/a/text()"
    column = "//div[@class='crumbs']/a[3]/text()"
    imgurl = '//div[@class="artText clearfix"]/p/i/a/img/@src'