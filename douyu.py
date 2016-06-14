#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re,threading,time
import requests
import mysql

#1斗鱼2熊猫3全民直播4虎牙直播
reload(sys)
sys.setdefaultencoding('utf-8')

####1斗鱼####
def douyu(one):
    my = mysql.MyDB()
    #ajax请求分页 一页24*5=120个主播
    #http://www.douyu.com/directory/game/LOL?page=2&isAjax=1
    headers  = {"Host":"www.douyu.com","Referer":"http://www.douyu.com","User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    base_url = "http://www.douyu.com/"

    gtype = one['id']
    if one['page'] > 1:
        gurl  = one['url']+'?page='+str(one['page'])+'&isAjax=1'
    else:
        gurl  = one['url']
    res   = requests.get(gurl,headers = headers,timeout = 15)
    if one['page'] == 1:
        com   = re.compile('<ul.*?id="live-list-contentbox".*?>(.*?)</ul>',re.S)
        con   = re.findall(com,res.text)
        com1  = re.compile('<li.*?data-rid=\'(.*?)\'>.*?<a.*?href="/(.*?)".*?title="(.*?)".*?>.*?<img.*?data-original="(.*?)".*?>.*?<div.*?class="mes">.*?<span.*?class="tag ellipsis">(.*?)</span>.*?</div>.*?<p>.*?<span.*?class="dy-name ellipsis fl">(.*?)</span>.*?<span.*?class="dy-num fr">(.*?)</span>.*?</p>.*?</div>.*?</a>.*?</li>',re.S)
        con1  = re.findall(com1,con[0])
    else:
        com1  = re.compile('<li.*?data-rid=\'(.*?)\'>.*?<a.*?href="/(.*?)".*?title="(.*?)".*?>.*?<img.*?data-original="(.*?)".*?>.*?<div.*?class="mes">.*?<span.*?class="tag ellipsis">(.*?)</span>.*?</div>.*?<p>.*?<span.*?class="dy-name ellipsis fl">(.*?)</span>.*?<span.*?class="dy-num fr">(.*?)</span>.*?</p>.*?</div>.*?</a>.*?</li>',re.S)
        con1  = re.findall(com1,res.text)
    page  = one['page'] + 1
    for item in con1:
        rid     = item[0]#房间id
        uid     = item[1]#用户id，专属域名
        rname   = my.escape_string(item[2])#房间名
        img     = item[3]#缩略图
        #gtype   = item[4]#游戏分类
        uname   = item[5]#主播名
        see     = item[6]#房间用户数
        url     = base_url+item[0]
        if '万' in see:
            see = int(float(see[0:len(see)-1])*10000)
        find    = my.getOne("select * from zhibo where uid = '%s' and type = 1"%(uid))
        nowtime = getDatetime()
        if find:
            sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(see,img,nowtime,rname,find['id'])
            my.updateData(sql)
        else:
            sql  = "insert into zhibo (uid,rid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uid,rid,uname,rname,url,img,see,1,gtype,1,nowtime,nowtime)
            my.insertData(sql)
    if len(con1) == 120:
        time.sleep(1.5)
        douyu({'url':one['url'],'id':gtype,'page':page})

#获取当前日期时间，格式2007-06-02 04:55:02
def getDatetime():
    return time.strftime( '%Y-%m-%d %X', time.localtime() )

def startGo():
    threads = []
    all_arr = {
            'wow':{'url':'http://www.douyu.com/directory/game/WOW','id':1,'page':1},
            'lol':{'url':'http://www.douyu.com/directory/game/LOL','id':2,'page':1},
            'how':{'url':'http://www.douyu.com/directory/game/How','id':3,'page':1},
            'hszz':{'url':'http://www.douyu.com/directory/game/hszz','id':4,'page':1},
            'overwatch':{'url':'http://www.douyu.com/directory/game/Overwatch','id':5,'page':1},
            'dota2':{'url':'http://www.douyu.com/directory/game/DOTA2','id':6,'page':1}
            }
    my = mysql.MyDB()
    for pt in all_arr.keys():
        upsql = "update zhibo set online = 0 where type = 1 and gtype = %d"%(all_arr[pt]['id'])
        my.updateData(upsql)
        thr = threading.Thread(target=douyu,args=(all_arr[pt],))
        threads.append(thr)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    startGo()