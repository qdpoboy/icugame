#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
import sys
import requests
import mysql

reload(sys)
sys.setdefaultencoding('utf-8')

my  = mysql.MyDB()
res = requests.get("http://wow.17173.com/news/wodnews.shtml")
content = res.text

com = re.compile('<ul class="gb-list1 article-list js-divide5">(.*?)</ul>',re.S)
con = re.findall(com,content)

com1 = re.compile('<li><span class="author">(.*?)</span><span class="date">(.*?)</span><span class="tit"><a href="(.*?)" target="_blank".*?>(.*?)</a></span></li>',re.S)
con1 = re.findall(com1,con[0])

for item in con1:
    sql = "insert into wow (title,url,author,date) values('%s','%s','%s','%s')"%(item[3],item[2],item[0],item[1])
    my.insertData(sql);