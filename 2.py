#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re,threading,time
import requests
import mysql

#1斗鱼2熊猫3全民直播4虎牙直播
#目前未分页抓取，只抓取了首页
reload(sys)
sys.setdefaultencoding('utf-8')

####斗鱼####
def douyu():
    #ajax请求分页 一页24*5=120个主播
    #http://www.douyu.com/directory/game/LOL?page=2&isAjax=1
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
            url     = base_url+item[0]
            see_num = item[5]
            if '万' in item[5]:
                see_num = int(float(item[5][0:len(item[5])-1])*10000)
            find    = my.getOne("select * from zhibo where type = 1 and uid = '%s'"%(item[0]))
            nowtime = getDatetime()
            if find:
                sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s' where id = %d"%(see_num,item[2],nowtime,find['id'])
                my.updateData(sql)
            else:
                sql  = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item[0],item[4],item[1],url,item[2],see_num,1,gtype,1,nowtime,nowtime)
                my.insertData(sql)

####熊猫####
def panda():
    #ajax请求分页  一页24*5=120个主播
    #http://www.panda.tv/ajax_sort?token=&pageno=2&pagenum=120&classification=lol&_=1464333261918
    headers  = {"Host":"www.panda.tv","Referer":"http://www.panda.tv","User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    base_url = "http://www.panda.tv/"

    all_arr  = {
                'wow':{'url':'http://www.panda.tv/cate/wow','id':1},
                'lol':{'url':'http://www.panda.tv/cate/lol','id':2},
                'how':{'url':'http://www.panda.tv/cate/hearthstone','id':3}
                }

    for one in all_arr.keys():
        gtype = all_arr[one]['id']
        gurl  = all_arr[one]['url']
        res   = requests.get(gurl,headers = headers)

        com   = re.compile('<li.*?class="video-list-item video-no-tag video-no-cate".*?>.*?<a.*?href="/(.*?)".*?class="video-list-item-wrap".*?>.*?<div.*?class="video-cover">.*?<img.*?data-original="(.*?)".*?>.*?</div>.*?<div.*?class="video-title".*?>(.*?)</div>.*?<div.*?class="video-info">.*?<span.*?class="video-nickname">(.*?)</span>.*?<span.*?class="video-number">(.*?)</span>.*?</div>.*?</a>.*?</li>',re.S)
        con   = re.findall(com,res.content)
        my    = mysql.MyDB()
        upsql = "update zhibo set online = 0 where type = 2 and gtype = %d"%(gtype)
        my.updateData(upsql)
        for item in con:
            #print item[0]#用户id，专属域名
            #print item[1]#缩略图
            #print item[2]#房间名
            #print item[3]#主播名
            #print item[4]#房间用户数
            #print "\n"
            url     = base_url+item[0]
            find    = my.getOne("select * from zhibo where type = 2 and uid = '%s'"%(item[0]))
            nowtime = getDatetime()
            if find:
                sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s' where id = %d"%(item[4],item[1],nowtime,find['id'])
                my.updateData(sql)
            else:
                sql = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item[0],item[3],item[2],url,item[1],item[4],2,gtype,1,nowtime,nowtime)
                my.insertData(sql)

####全民####
def quanmin():
    print 'quanmin'

####虎牙####
def huya():
    print 'huya'

#获取当前日期时间，格式2007-06-02 04:55:02
def getDatetime():
    return time.strftime( '%Y-%m-%d %X', time.localtime() )

def startGet(n):
    print n
    if n==1:
        douyu()
    elif n==2:
        panda()
    elif n==3:
        quanmin()
    elif n==4:
        huya()

def startGo():
    threads = []
    for pt in (1,2,3,4):
        thr = threading.Thread(target=startGet,args=(pt,))
        threads.append(thr)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    startGo()
    #startGet(2)