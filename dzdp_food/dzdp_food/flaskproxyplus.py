# -*-coding=utf-8-*-
import requests
import json


class httpProxyMiddleware(object):

    def __init__(self):
        self.get_ip_url = "http://139.162.99.142:5000"
        self.proxy_ip = self.getProxyIp()
        self.pppoe_flag = True

    def process_request(self, request, spider):
        # request.meta['proxy'] = 'http://{}'.format("60.179.41.59:1080")
        request.meta['proxy'] = 'http://{}'.format(self.proxy_ip)
        print self.proxy_ip
        return None

    def process_response(self, request, response, spider):
        if response.status in [403, 400]:
            self.proxy_ip = self.getProxyIp()
            fail_res = request.copy()
            fail_res.dont_filter = True
            return fail_res
        return response

    def getProxyIp(self):
        return requests.get(url=self.get_ip_url, auth=('icaruslou', 'f3d9c92b3ea1959ddb0f5140eb5caaec'), timeout=30).text

    def process_exception(self, request, exception, spider):
        print 'run________'
        self.proxy_ip = self.getProxyIp()
        fail_res = request.copy()
        fail_res.dont_filter = True
        return fail_res

    # def __del__(self):
    #     self.ssh.close()
