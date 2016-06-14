#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re,threading,time,json
import requests
import mysql

#1斗鱼2熊猫3全民直播4虎牙直播
reload(sys)
sys.setdefaultencoding('utf-8')

####2熊猫####
def panda(one):
    #ajax请求分页  一页24*5=120个主播
    #http://www.panda.tv/ajax_sort?token=&pageno=2&pagenum=120&classification=lol&_=1464333261918
    headers  = {"Host":"www.panda.tv","Referer":"http://www.panda.tv","User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    base_url = "http://www.panda.tv/"

    gtype = one['id']
    my    = mysql.MyDB()
    page  = one['page'] + 1
    if one['page'] == 1:
        gurl  = one['url']
        res   = requests.get(gurl,headers = headers)
        com   = re.compile('<li.*?class="video-list-item video-no-tag video-no-cate".*?>.*?<a.*?href="/(.*?)".*?class="video-list-item-wrap".*?>.*?<div.*?class="video-cover">.*?<img.*?data-original="(.*?)".*?>.*?</div>.*?<div.*?class="video-title".*?>(.*?)</div>.*?<div.*?class="video-info">.*?<span.*?class="video-nickname">(.*?)</span>.*?<span.*?class="video-number">(.*?)</span>.*?</div>.*?</a>.*?</li>',re.S)
        con   = re.findall(com,res.content)
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
                sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(item[4],item[1],nowtime,my.escape_string(item[2]),find['id'])
                my.updateData(sql)
            else:
                sql = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(item[0],item[3],my.escape_string(item[2]),url,item[1],item[4],2,gtype,1,nowtime,nowtime)
                my.insertData(sql)
    else:
        gurl  = base_url+'ajax_sort?token=&pageno='+str(one['page'])+'&pagenum=120&classification='+one['page_class']+'&_='+str(time.time())
        res   = requests.get(gurl,headers = headers)
        con   = json.loads(res.content)['data']['items']
        for item in con:
            uid     = item['id']
            img     = item['pictures']['img']
            uname   = item['userinfo']['nickName']
            rname   = my.escape_string(item['name'])
            see     = item['person_num']
            url     = base_url+uid
            find    = my.getOne("select * from zhibo where uid = '%s' and type = 2"%(uid))
            nowtime = getDatetime()
            if find:
                sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(see,img,nowtime,rname,find['id'])
                my.updateData(sql)
            else:
                sql = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uid,uname,rname,url,img,see,2,gtype,1,nowtime,nowtime)
                my.insertData(sql)
        
    if len(con) != 0:
        time.sleep(1)
        panda({'url':one['url'],'id':gtype,'page':page,'page_class':one['page_class']})

#获取当前日期时间，格式2007-06-02 04:55:02
def getDatetime():
    return time.strftime( '%Y-%m-%d %X', time.localtime() )

def startGo():
    threads = []
    all_arr = {
            'wow':{'url':'http://www.panda.tv/cate/wow','id':1,'page':1,'page_class':'wow'},
            'lol':{'url':'http://www.panda.tv/cate/lol','id':2,'page':1,'page_class':'lol'},
            'how':{'url':'http://www.panda.tv/cate/hearthstone','id':3,'page':1,'page_class':'hearthstone'},
            'hszz':{'url':'http://www.panda.tv/cate/clashroyale','id':4,'page':1,'page_class':'clashroyale'},
            'overwatch':{'url':'http://www.panda.tv/cate/overwatch','id':5,'page':1,'page_class':'overwatch'},
            'dota2':{'url':'http://www.panda.tv/cate/dota2','id':6,'page':1,'page_class':'dota2'},
            }
    my = mysql.MyDB()
    for pt in all_arr.keys():
        upsql = "update zhibo set online = 0 where type = 2 and gtype = %d"%(all_arr[pt]['id'])
        my.updateData(upsql)
        thr = threading.Thread(target=panda,args=(all_arr[pt],))
        threads.append(thr)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    startGo()