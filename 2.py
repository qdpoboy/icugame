#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import re
import requests
import mysql

reload(sys)
sys.setdefaultencoding('utf-8')

headers  = {"Host":"www.douyu.com","Referer":"http://www.douyu.com","User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}

base_url = "http://www.douyu.com/"

all_arr  = {
            'wow':{'url':'http://www.douyu.com/directory/game/WOW','id':1},
            'lol':{'url':'http://www.douyu.com/directory/game/LOL','id':2},
            'how':{'url':'http://www.douyu.com/directory/game/How','id':3}
            }

for one in all_arr.keys():
    gtype = all_arr[one]['id']
    gurl  = all_arr[one]['url']
    res   = requests.get(gurl,headers = headers)

    com   = re.compile('<ul.*?id="live-list-contentbox".*?>(.*?)</ul>',re.S)
    con   = re.findall(com,res.text)
    com1  = re.compile('<li.*?>.*?<a.*?href="/(.*?)".*?title="(.*?)".*?>.*?<img.*?data-original="(.*?)".*?>.*?<div.*?class="mes">.*?<span.*?class="tag ellipsis">(.*?)</span>.*?</div>.*?<p>.*?<span.*?class="dy-name ellipsis fl">(.*?)</span>.*?<span.*?class="dy-num fr">(.*?)</span>.*?</p>.*?</div>.*?</a>.*?</li>',re.S)
    con1  = re.findall(com1,con[0])

    my    = mysql.MyDB()
    upsql = "update zhibo set online = 0 where type = 1 and gtype = %d"%(gtype)
    my.updateData(upsql)
    for item in con1:
        #print item[0]#用户id，专属域名
        #print item[1]#房间名
        #print item[2]#缩略图
        #print item[3]#游戏分类
        #print item[4]#主播名
        #print item[5]#房间用户数
        #print "\n"
        url  = base_url+item[0]
        find = my.getOne("select * from zhibo where uid = '%s'"%(item[0]))
        if find:
            sql = "update zhibo set see = '%s',online = 1 where id = %d"%(item[5],find['id'])
            my.updateData(sql)
        else:
            sql  = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item[0],item[4],item[1],url,item[2],item[5],1,gtype,1)
            my.insertData(sql)