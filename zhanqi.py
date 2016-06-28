#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re,threading,time,json
import requests
import mysql

reload(sys)
sys.setdefaultencoding('utf-8')

####5战旗####
def zhanqi(one):
    my = mysql.MyDB()
    #ajax请求分页 一页6*5=120个主播
    #http://www.zhanqi.tv/90god
    headers  = {"Host":"www.zhanqi.tv","Referer":"http://www.zhanqi.tv","User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    base_url = "http://www.zhanqi.tv/"

    gtype = one['id']
    if one['page'] > 1:
        gurl  = one['url']+'?page='+str(one['page'])+'&isAjax=1'
    else:
        gurl  = one['url']
    res   = requests.get(gurl,headers = headers,timeout = 15)
    if one['page'] == 1:
        if (gtype == 1 or gtype == 3 or gtype == 5):#暴雪的游戏
            com   = re.compile('<ul.*?class="clearfix gameList".*?class="clearfix".*?data-width=".*?">(.*?)</ul>',re.S)
            con   = re.findall(com,res.text)
            com1  = re.compile('<li.*?data-room-id="(.*?)".*?>.*?<a href="/(.*?)".*?class="js-jump-link">.*?<div.*?class="imgBox".*?>.*?<img.*?src="(.*?)".*?>.*?</div>.*?<div.*?class="info-area">.*?<span.*?class="name".*?>(.*?)</span>.*?<div.*?class="meat">.*?<span.*?class="views">.*?<span.*?class="dv">(.*?)</span>.*?</span>.*?<span.*?class="anchor anchor-to-cut dv".*?>(.*?)</span>.*?<span.*?class="game-name dv".*?>(.*?)</span>.*?</div>.*?</div>.*?</a>.*?</li>',re.S)
            con1  = re.findall(com1,con[one['con_key']])
        else:
            com   = re.compile('<ul.*?class="clearfix js-room-list-ul".*?data-width=".*?">(.*?)</ul>',re.S)
            con   = re.findall(com,res.text)
            com1  = re.compile('<li.*?data-room-id="(.*?)".*?>.*?<a href="/(.*?)".*?class="js-jump-link">.*?<div.*?class="imgBox".*?>.*?<img.*?src="(.*?)".*?>.*?</div>.*?<div.*?class="info-area">.*?<span.*?class="name".*?>(.*?)</span>.*?<div.*?class="meat">.*?<span.*?class="views">.*?<span.*?class="dv">(.*?)</span>.*?</span>.*?<span.*?class="anchor anchor-to-cut dv".*?>(.*?)</span>.*?<span.*?class="game-name dv".*?>(.*?)</span>.*?</div>.*?</div>.*?</a>.*?</li>',re.S)
            con1  = re.findall(com1,con[0])

        for item in con1:
            rid     = item[0]#房间id
            uid     = item[1]#用户id，专属域名
            rname   = my.escape_string(item[3])#房间名
            img     = item[2]#缩略图
            #gtype   = item[6]#游戏分类
            uname   = item[5]#主播名
            see     = item[4]#房间用户数
            url     = base_url+item[1]
            if '万' in see:
                see = int(float(see[0:len(see)-1])*10000)
            find    = my.getOne("select * from zhibo where uid = '%s' and type = 5"%(uid))
            nowtime = getDatetime()
            if find:
                sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(see,img,nowtime,rname,find['id'])
                my.updateData(sql)
            else:
                sql  = "insert into zhibo (uid,rid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uid,rid,uname,rname,url,img,see,5,gtype,1,nowtime,nowtime)
                my.insertData(sql)
    else:
        gurl  = base_url+'api/static/game.lives/'+str(one['page_key'])+'/30-'+str(one['page'])+'.json'
        res   = requests.get(gurl,headers = headers)
        if res.content is None:
            con1 = {}
        else:
            con1  = json.loads(res.content)['data']['rooms']
            for item in con1:
                rid     = item['id']#房间id
                uid     = item['url']#用户id，专属域名
                rname   = my.escape_string(item['title'])#房间名
                img     = item['bpic']#缩略图
                #gtype   = item['gameName']#游戏分类gameId
                uname   = item['nickname']#主播名
                see     = item['online']#房间用户数
                url     = base_url+item['url']
                find    = my.getOne("select * from zhibo where uid = '%s' and type = 5"%(uid))
                nowtime = getDatetime()
                if '万' in see:
                    see = int(float(see[0:len(see)-1])*10000)
                if find:
                    sql = "update zhibo set see = '%s',online = 1,img = '%s',uptime = '%s',rname = '%s' where id = %d"%(see,img,nowtime,rname,find['id'])
                    my.updateData(sql)
                else:
                    sql  = "insert into zhibo (uid,rid,uname,rname,url,img,see,type,gtype,online,addtime,uptime) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uid,rid,uname,rname,url,img,see,5,gtype,1,nowtime,nowtime)
                    my.insertData(sql)

    page  = one['page'] + 1
    if len(con1) == 30:
        time.sleep(1.5)
        zhanqi({'url':one['url'],'id':gtype,'page':page,'con_key':one['con_key'],'page_key':one['page_key']})

#获取当前日期时间，格式2007-06-02 04:55:02
def getDatetime():
    return time.strftime( '%Y-%m-%d %X', time.localtime() )

def startGo():
    threads = []
    all_arr = {
            'wow':{'url':'http://www.zhanqi.tv/chns/blizzard/wow','id':1,'page':1,'con_key':3,'page_key':8},
            'lol':{'url':'http://www.zhanqi.tv/games/lol','id':2,'page':1,'con_key':0,'page_key':6},
            'how':{'url':'http://www.zhanqi.tv/chns/blizzard/how','id':3,'page':1,'con_key':1,'page_key':9},
            #'hszz':{'url':'http://www.zhanqi.tv/games/ClashRoyale','id':4,'page':1,'con_key':0,'page_key':8},#战旗下面没有主播
            'overwatch':{'url':'http://www.zhanqi.tv/chns/blizzard/watch','id':5,'page':1,'con_key':2,'page_key':82},
            'dota2':{'url':'http://www.zhanqi.tv/games/dota2','id':6,'page':1,'con_key':0,'page_key':10}
            }
    my = mysql.MyDB()
    for pt in all_arr.keys():
        upsql = "update zhibo set online = 0 where type = 5 and gtype = %d"%(all_arr[pt]['id'])
        my.updateData(upsql)
        thr = threading.Thread(target=zhanqi,args=(all_arr[pt],))
        threads.append(thr)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    startGo()