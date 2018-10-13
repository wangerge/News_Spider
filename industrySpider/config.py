# -*- coding: utf-8 -*-

MYSQL_URL = '',
USER = '',
PASSWORD = '',
MYSQL_DB = 'th_spider_database',
MYSQL_TABLE = 'data_set'

SQL = 'insert into data_set (id, title, noteDate, htmlContent, tags, circleKey, coverPic, coverPicType, src) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'