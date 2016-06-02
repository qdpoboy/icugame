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
    res   = requests.get(gurl,headers = headers,timeout = 10)
    if one['page'] == 1:
        com   = re.compile('<ul.*?id="live-list-contentbox".*?>(.*?)</ul>',re.S)
        con   = re.findall(com,res.text)
        com1  = re.compile('<li.*?>.*?<a.*?href="/(.*?)".*?title="(.*?)".*?>.*?<img.*?data-original="(.*?)".*?>.*?<div.*?class="mes">.*?<span.*?class="tag ellipsis">(.*?)</span>.*?</div>.*?<p>.*?<span.*?class="dy-name ellipsis fl">(.*?)</span>.*?<span.*?class="dy-num fr">(.*?)</span>.*?</p>.*?</div>.*?</a>.*?</li>',re.S)
        con1  = re.findall(com1,con[0])
    else:
        com1  = re.compile('<li.*?>.*?<a.*?href="/(.*?)".*?title="(.*?)".*?>.*?<img.*?data-original="(.*?)".*?>.*?<div.*?class="mes">.*?<span.*?class="tag ellipsis">(.*?)</span>.*?</div>.*?<p>.*?<span.*?class="dy-name ellipsis fl">(.*?)</span>.*?<span.*?class="dy-num fr">(.*?)</span>.*?</p>.*?</div>.*?</a>.*?</li>',re.S)
        con1  = re.findall(com1,res.text)
    
    page  = one['page'] + 1
    for item in con1:
        #print item[0]#用户id，专属域名
        #print item[1]#房间名
        #print item[2]#缩略图
        #print item[3]#游戏分类
        #print item[4]#主播名
        #print item[5]#房间用户数
        #print "\n"
        url     = base_url+item[0]
        see_num = item[5]
        if '万' in item[5]:
            see_num = int(float(item[5][0:len(item[5])-1])*10000)
        find    = my.getOne("select * from zhibo where type = 1 and uid = '%s'"%(item[0]))
        nowtime = getDatetime()
        if find:
            sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(see_num,item[2],nowtime,item[1],find['id'])
            my.updateData(sql)
        else:
            sql  = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item[0],item[4],item[1],url,item[2],see_num,1,gtype,1,nowtime,nowtime)
            my.insertData(sql)
    if len(con1) == 120:
        douyu({'url':one['url'],'id':1,'page':page})

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
            'overwatch':{'url':'http://www.douyu.com/directory/game/Overwatch','id':5,'page':1}
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