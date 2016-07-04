#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re,time,threading
import requests
import mysql

reload(sys)
sys.setdefaultencoding('utf-8')

def main(one):
    headers  = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    my  = mysql.MyDB()
    if one['page'] == 1:
        url = one['url'] + '.shtml'
    else:
        url = one['url'] + '_' + str(one['page']) + '.shtml'
    res = requests.get(url,headers = headers,timeout = 15)
    content = res.text.encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(res.text)[0])

    com1 = re.compile('<div class="article-item">.*?<div class="tit"><a href="(.*?)".*?>(.*?)</a>.*?</div>.*?<p class="info"><span class="date">(.*?)</span>.*?<span class="auto">(.*?)</span>.*?</p>.*?<p class="con">(.*?)<a.*?>.*?</a>.*?</p>.*?</div>',re.S)
    con1 = re.findall(com1,content)

    for item in con1:
        d_url    = item[0]
        d_title  = item[1]
        d_date   = item[2]
        d_author = item[3][3:]
        d_des    = item[4]
        addtime  = getDatetime()
        sql = "insert into gonglue (title,url,author,date,type,gtype,addtime) values('%s','%s','%s','%s','%s','%s','%s')"%(d_title,d_url,d_author,d_date,1,3,addtime)
        my.insertData(sql);

    page = one['page'] + 1
    if page == 100:
        exit()
    if len(con1) == 10:
        main({'url':'http://hs.17173.com/list2014/zhiye','id':1,'page':page})

def wow():
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

def getDatetime():
    return time.strftime( '%Y-%m-%d %X', time.localtime() )


def startGo():
    threads = []
    all_arr = {
            'zhiye':{'url':'http://hs.17173.com/list2014/zhiye','id':1,'page':1},
            #'lol':{'url':'http://wow.17173.com/news/wodnews.shtml','id':2,'page':1},
            #'how':{'url':'http://www.douyu.com/directory/game/How','id':3,'page':1},
            #'hszz':{'url':'http://www.douyu.com/directory/game/hszz','id':4,'page':1},
            #'overwatch':{'url':'http://www.douyu.com/directory/game/Overwatch','id':5,'page':1},
            #'dota2':{'url':'http://www.douyu.com/directory/game/DOTA2','id':6,'page':1}
            }
    for pt in all_arr.keys():
        thr = threading.Thread(target=main,args=(all_arr[pt],))
        threads.append(thr)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == '__main__':
    startGo()