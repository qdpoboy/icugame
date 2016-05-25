#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import re
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

url = "http://www.douyu.com/directory/game/LOL"

res = requests.get(url)

print res.text