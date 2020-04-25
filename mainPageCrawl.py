# -*- coding:UTF-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import time
import numpy as np
import urllib
import os
from functools import reduce

# A function for setting HTTP headers
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

# A function for setting HTTP Cookie
cookies = {
  'Cookie': '__utmz=10187688.1586613271.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none); __gads=ID=f252e081be9b198e:T=1586613273:S=ALNI_MZBSjzKzeFxnV1T56a9uNvtVqIcaA; __utma=10187688.1826147105.1586613271.1587390954.1587814661.7; __utmb=10187688; __utmc=10187688'
}

REG_URL = r'^(https?://|//)?((?:[a-zA-Z0-9-_]+\.)+(?:[a-zA-Z0-9-_:]+))((?:/[-_.a-zA-Z0-9]*?)*)((?<=/)[-a-zA-Z0-9]+(?:\.([a-zA-Z0-9]+))+)?((?:\?[a-zA-Z0-9%&=]*)*)$'
regUrl = re.compile(REG_URL)

'''
解析URL地址
'''
def parseUrl(url):
  if not url:
    return
  
  res = regUrl.search(url)
  # 在这里，我们把192.168.1.109:8080的形式也解析成域名domain，实际过程中www.baidu.com等才是域名，192.168.1.109只是IP地址
  # ('http://', '192.168.1.109:8080', '/abc/images/111/', 'index.html', 'html', '?a=1&b=2')
  if res is not None:
    path = res.group(3)
    fullPath = res.group(1) + res.group(2) + res.group(3)
  
  if not path.endswith('/'):
    path = path + '/'
    fullPath = fullPath + '/'
  
  return dict(
    baseUrl=res.group(1) + res.group(2),
    fullPath=fullPath,
    protocol=res.group(1),
    domain=res.group(2),
    path=path,
    fileName=res.group(4),
    ext=res.group(5),
    params=res.group(6)
  )

'''
解析路径

eg:
    basePath => F:\Programs\python\python-spider-downloads
    resourcePath => /a/b/c/ or a/b/c

    return => F:\Programs\python\python-spider-downloads\a\b\c
'''
def resolvePath(basePath, resourcePath):
  # 解析资源路径
  res = resourcePath.split('/')
  # 去掉空目录 /a/b/c/ => [a, b, c]
  dirList = list(filter(lambda x: x, res))

  # 目录不为空
  if dirList:
    # 拼接出绝对路径
    resourcePath = reduce(lambda x, y: os.path.join(x, y), dirList)
    dirStr = os.path.join(basePath, resourcePath)
  else:
    dirStr = basePath
  
  return dirStr

'''
下载文件
'''
def downloadFile(srcPath, distPath):
  downloadedList = []

  if distPath in downloadedList:
    return
  try:
    response = urllib.request.urlopen(srcPath)
    if response is None or response.status != 200:
        return print('> 请求异常：', srcPath)
    data = response.read()

    f = open(distPath, 'wb')
    f.write(data)
    f.close()

    downloadedList.append(distPath)

  except Exception as e:
    print('报错了：', e)

def crawlFun():
  # 读取网页内容
  url = 'http://www.linuxfromscratch.org/'
  headers = setHeaders()
  req = requests.post(url = url, headers = headers, cookies = cookies)
  req.encoding = 'utf-8'
  html = req.text # getting the request's result in text

  # 下载路径
  SAVE_PATH = os.path.join(os.path.abspath('.'), 'linuxfromscratch-downloads')
  # 创建这个站点的文件夹
  urlDict = parseUrl(url)
  print('分析的域名：', urlDict)
  domain = urlDict['domain']

  filePath = time.strftime('%Y-%m-%d', time.localtime()) + '-' + domain
  # 如果是192.168.1.1:8000等形式，变成192.168.1.1-8000，:不可以出现在文件名中
  filePath = re.sub(r':', '-', filePath)
  SAVE_PATH = os.path.join(SAVE_PATH, filePath)

  # 把网站的内容写下来
  pageName = ''
  if urlDict['fileName'] is None:
    pageName = 'index.html'
  else:
    pageName = urlDict['fileName']

  # 创建网页存放路径
  pageIndexDir = resolvePath(SAVE_PATH, urlDict['path'])
  if not os.path.exists(pageIndexDir):
    os.makedirs(pageIndexDir)
  
  # 保存网页
  pageIndexPath = os.path.join(pageIndexDir, pageName)
  print('主页的地址:', pageIndexPath)
  f = open(pageIndexPath, 'wb')
  f.write(html)
  f.close()

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

  # 下载资源，要区分目录，不存在的话就创建
  for resourceUrl in resourceList:
    # 下面是对资源链接进行处理
    if resourceUrl.startswith('./'):
      resourceUrl = urlDict['fullPath'] + resourceUrl[1:]
    elif resourceUrl.startswith('//'):
      resourceUrl = 'https:' + resourceUrl
    elif resourceUrl.startswith('/'):
      resourceUrl = urlDict['baseUrl'] + resourceUrl
    elif resourceUrl.startswith('http') or resourceUrl.startswith('https'):
      # 不处理，这是我们想要的url格式
      pass
    elif not (resourceUrl.startswith('http') or resourceUrl.startswith('https')):
      # static/js/index.js这种情况
      resourceUrl = urlDict['fullPath'] + resourceUrl
    else:
      print('> 未知resource url: %s' % resourceUrl)

    # 对每个规范的资源链接进行解析（parseUrl），提取出它要存放的目录和文件名等等，然后创建对应的目录
    # 解析文件，查看文件路径
    resourceUrlDict = parseUrl(resourceUrl)
    if resourceUrlDict is None:
      print('> 解析文件出错：%s' % resourceUrl)
      continue

    resourceDomain = resourceUrlDict['domain']
    resourcePath = resourceUrlDict['path']
    resourceName = resourceUrlDict['fileName']

    if resourceDomain != domain:
      print('> 该资源不是本网站的，也下载：', resourceDomain)
      # 如果下载的话，根目录就要变了
      # 再创建一个目录，用于保存其他地方的资源
      resourceDomain =  re.sub(r':', '-', resourceDomain)
      savePath = os.path.join(SAVE_PATH, resourceDomain)
      if not os.path.exists(SAVE_PATH):
        print('> 目标目录不存在，创建：', savePath)
        os.makedirs(savePath)
    else:
      savePath = SAVE_PATH

    # 解析资源路径
    dirStr = resolvePath(savePath, resourcePath)

    if not os.path.exists(SAVE_PATH):
        print('> 目标目录不存在，创建：', savePath)
        os.makedirs(savePath)

    # 写入文件
    downloadFile(resourceUrl, os.path.join(dirStr, resourceName))

  print('-----------------下载完成------------------')
  print('总共下载了%d个资源' % len(resourceList))

# main function
if __name__ == '__main__':
  crawlFun()
  print('Success!!!')