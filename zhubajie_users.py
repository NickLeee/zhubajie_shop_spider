# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 20:13:18 2016

@author: lenovo
"""
import urllib2
from bs4 import BeautifulSoup
import re
import MySQLdb
import time
url = 'http://home.zbj.com/'
def getpage(url):
    try:
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        request = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(request)
        content = response.read()
        soup = BeautifulSoup(content)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print e.reason
    return soup

#类别获取
def getmenu(url):
    menulist = []
    soup1 = getpage(url)
    menu =  soup1.find_all('ul',class_='unstyled ui-dropdown-menu')
    for menuitem in menu[1].find_all('a'):
        menuitemtemp = re.findall('com/(.+?)/p',menuitem.attrs['href'])[0]
        menulist.append(menuitemtemp)
    return menulist
    

#获取有保障金服务商数量477
'''
    menupagenumber = {}
    for menuitemuse in menulist:
        urllist = 'http://www.zbj.com/'+menuitemuse+'/pu1s3b1p1.html'
        souplist = getpage(urllist)
        pagenumber = str(souplist.find_all('a',attrs={"href":re.compile('.*?pu1s.*?')})[-2].text)
        menupagenumber[menuitemuse] = int(pagenumber)
'''
    



def getpageshoplist(soup):
    shopitems = []
    h5 = soup.find_all('h5',class_='fws-detail-hd')
    for items in h5:
        shopurl = items.contents[0].attrs['href']
        shopid = re.findall('http://shop.zbj.com/(\d+)',shopurl)[0]
        shopname = items.contents[0].attrs['title']
        shop3item = [shopid,shopname,shopurl]
        shopitems.append(shop3item)
    return shopitems
    
def writeSQL(shopitems):
    conn = MySQLdb.Connect(host='localhost', user='root', passwd='123456', db='zhubajie',charset='utf8')
    cur=conn.cursor()
    for item in shopitems:
        cur.execute('insert ignore into shopurllist values(%s,%s,%s)',item)
    conn.commit()
    cur.close()
    return
    

#urltest = 'http://www.zbj.com/yxtg/pu1s3b1.html'

#shop = getpageshoplist(urltest)
#writeSQL(shop)

#print '读取类别'
menulist = ['ppsj','wzkf','wdfw','paperwork','cyqm','yidongkf','rjkf','uisheji','game','dhmh','gongyesj','fzpssj','zhuangxiu','gc','zrfw','qyfw','video','consult','jsfw','shichangdc','ys','sysx','music']
for menu in menulist:
#print '读取类别完成'
    urlstart = 'http://www.zbj.com/'+menu+'/pu1s3b1p1.html'
    print ('获取%s类第1页'%(menu))
    soup1 = getpage(urlstart)
    menupagemunber = str(soup1.find_all('a',attrs={"href":re.compile('.*?pu1s.*?')})[-2].text)
    shop1 = getpageshoplist(soup1)
    print ('%s类第1页写入SQL'%(menu))
    writeSQL(shop1)
    time.sleep(3)
    for i in range(int(menupagemunber)-1):
        urlothers = 'http://www.zbj.com/'+menu+'/pu1s3b1p'+str(i+2)+'.html'
        print ('获取%s类第%d页'%(menu,i+2))    
        soup = getpage(urlothers)
        shop = getpageshoplist(soup)
        print ('%s类第%d页写入SQL'%(menu,i+2))    
        writeSQL(shop)
        time.sleep(3)








