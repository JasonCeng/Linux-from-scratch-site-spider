import os
from functools import reduce
import re
import requests
import urllib

def setHeaders():
  headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # 'Accept-Encoding': 'gzip, deflate, br', # if this line is added, the page will be garbled.
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.linuxfromscratch.org',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
  }
  return headers

cookies = {
  'Cookie': '__utmz=10187688.1586613271.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none); __gads=ID=f252e081be9b198e:T=1586613273:S=ALNI_MZBSjzKzeFxnV1T56a9uNvtVqIcaA; __utma=10187688.1826147105.1586613271.1587390954.1587814661.7; __utmb=10187688; __utmc=10187688'
}

REG_URL = r'^(https?://|//)?((?:[a-zA-Z0-9-_]+\.)+(?:[a-zA-Z0-9-_:]+))((?:/[-_.a-zA-Z0-9]*?)*)((?<=/)[-a-zA-Z0-9]+(?:\.([a-zA-Z0-9]+))+)?((?:\?[a-zA-Z0-9%&=]*)*)$'
regUrl = re.compile(REG_URL)

url = 'http://www.linuxfromscratch.org/'
headers = setHeaders()
req = requests.post(url = url, headers = headers, cookies = cookies)
req.encoding = 'utf-8'
print(req)
html = req.text
print(html)

# 提取有用的资源链接
# 资源链接匹配正则表达式
REG_RESOURCE_TYPE = r'(?:href|src|data\-original|data\-src)=["\'](.+?\.(?:js|css|jpg|jpeg|png|gif|svg|ico|ttf|woff2))[a-zA-Z0-9\?\=\.]*["\']'

# re.S代表开启多行匹配模式
regResouce = re.compile(REG_RESOURCE_TYPE, re.S)
# 解析网页内容，获取有效的链接
# html 是上一步读取到的网页内容
contentList = re.split(r'\s+', html)
resourceList = []
for line in contentList:
  resList = regResouce.findall(line)
  if resList is not None:
    resourceList = resourceList + resList

print(resourceList)