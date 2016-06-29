#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re,threading,time,json,random
import requests
import mysql

reload(sys)
sys.setdefaultencoding('utf-8')

####3全民####
def quanmin(one):
    my = mysql.MyDB()
    #http://www.quanmin.tv/json/categories/lol/list_3.json?t=24453074全民的分页
    headers  = {"Host":"www.quanmin.tv","Referer":"http://www.quanmin.tv","User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    base_url = "http://www.quanmin.tv/"

    gtype = one['id']
    if one['page'] > 1:
        gurl  = one['url']+'_'+str(one['page'])+'.json?t='+str(random.randint(10000000,99999999))
    else:
        gurl  = one['url']+'.json?t='+str(random.randint(10000000,99999999))
    res   = requests.get(gurl,headers = headers,timeout = 15)

    if res.content is None:
        con1 = {}
    else:
        con1  = json.loads(res.content)['data']
        for item in con1:
            uid     = item['uid']#全民取的用户id,未用专属域名(slug)
            rname   = my.escape_string(item['title'])#房间名
            img     = item['thumb']#缩略图
            #gtype   = item['gameName']#游戏分类gameId
            uname   = item['nick']#主播名
            see     = item['view']#房间用户数
            url     = base_url+'v/'+item['uid']
            find    = my.getOne("select * from zhibo where uid = '%s' and type = 3"%(uid))
            nowtime = getDatetime()
            if find:
                sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(see,img,nowtime,rname,find['id'])
                my.updateData(sql)
            else:
                sql  = "insert into zhibo (uid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uid,uname,rname,url,img,see,3,gtype,1,nowtime,nowtime)
                my.insertData(sql)

    page  = one['page'] + 1
    if len(con1) == 90:
        time.sleep(1.5)
        quanmin({'url':one['url'],'id':gtype,'page':page})

#获取当前日期时间，格式2007-06-02 04:55:02
def getDatetime():
    return time.strftime( '%Y-%m-%d %X', time.localtime() )

def startGo():
    threads = []
    #http://www.quanmin.tv/json/categories/lol/list_3.json?t=24453074
    all_arr = {
            'wow':{'url':'http://www.quanmin.tv/json/categories/blizzard/list','id':1,'page':1},
            'lol':{'url':'http://www.quanmin.tv/json/categories/lol/list','id':2,'page':1},
            'how':{'url':'http://www.quanmin.tv/json/categories/hearthstone/list','id':3,'page':1},
            'hszz':{'url':'http://www.quanmin.tv/json/categories/clashroyale/list','id':4,'page':1},
            'overwatch':{'url':'http://www.quanmin.tv/json/categories/overwatch/list','id':5,'page':1},
            'dota2':{'url':'http://www.quanmin.tv/json/categories/dota2/list','id':6,'page':1}
            }
    my = mysql.MyDB()
    for pt in all_arr.keys():
        upsql = "update zhibo set online = 0 where type = 3 and gtype = %d"%(all_arr[pt]['id'])
        my.updateData(upsql)
        thr = threading.Thread(target=quanmin,args=(all_arr[pt],))
        threads.append(thr)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    startGo()