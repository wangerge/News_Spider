# -*- coding: utf-8 -*-

import re
import base64
import pymysql
import requests
from .config import *
from io import BytesIO
from scrapy import Selector
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, RequestException

# noinspection PyPackageRequirements
database = pymysql.connect(MYSQL_URL[0],USER[0],PASSWORD[0],MYSQL_DB[0],use_unicode=True, charset="utf8")
cursor = database.cursor()
sql = SQL


class BaseSpider(object):
    def __init__(self):
        pass

    def decodehtml(req):
        if req.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(req.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = req.apparent_encoding

            # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
            global encode_content
            encode_content = req.content.decode(encoding, 'replace')  # 如果设置为replace，则会用?取代非法字符；
    def get_article_index(self,url,cookies='',headers='',proxies='',timeout=30,requestsMethod='get',data='',stream=False):
        # 请求索引页
        try:
            if requestsMethod == 'get':
                response = requests.get(url,cookies=cookies,headers=headers,proxies=proxies,timeout=timeout,stream=stream)
            else:
                response = requests.post(url,cookies=cookies,headers=headers,proxies=proxies,timeout=timeout,data=data)
            if response.status_code == 200:
                return response
            return None
        except ConnectionError:
            print('Error occurred')
            return None

    def parse_article_index(self,html,index_css_selector,info_css_selector):
        # 解析索引页
        try:
            selector = Selector(text=html)
            article_html_index = selector.css(index_css_selector['article'])
            for item in article_html_index:
                yield tuple(map(item.css,info_css_selector))
        except Exception as e:
            print(e)
            pass

    def get_article_detail(self,url,cookies='',headers='',proxies='',timeout=30,requestsMethod='get',data='',stream=True):
        # 请求文章
        try:
            if requestsMethod == 'get':
                response = requests.get(url,cookies=cookies,headers=headers,proxies=proxies,timeout=timeout,stream=stream)
            else:
                response = requests.post(url,cookies=cookies,headers=headers,proxies=proxies,timeout=timeout,data=data)
            if response.status_code == 200:
                return response
            return None
        except ConnectionError:
            print('Error occurred')
            return None

    def parse_article_detail(self,html,article_css_selector):
        # 解析文章
        try:
            selector = Selector(text=html)
            return tuple(map(selector.css,article_css_selector))
        except:
            pass

    def html_strip(self,html,stripItem):
        # 整理或清洗文章
        for item in stripItem:
            re_strip = re.compile(item[0], item[1])
            html = re_strip.sub(item[2], html)
        html = BeautifulSoup(html, 'lxml').prettify()

        re_html = re.compile('<html>', re.I)
        re_htmls = re.compile('</html>', re.I)
        html = re_html.sub('', html)
        html = re_htmls.sub('', html)
        return html

    def encode_img(self,url,cookies='',headers='',proxies='',timeout=30,stream=True):
        # 图片内容转换
        try:
            # response = requests.get(url, headers=headers,proxies=proxies,cookies=cookies,timeout=timeout,stream=stream)
            # if response.status_code == 200:
            #     return base64.b64encode(response.content), url.split('.')[-1]
            # return '', ''
            return url,url.split('?')[0].split('.')[-1]
        except RequestException:
            return '', ''

    def save_data(self,data):
        # 保存数据
        try:
            cursor.execute(sql, data)
            database.commit()
            print('insert ok')
            return True
        except Exception as e:
            print(e)
            print('insert erro')
            return False
            pass