# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:43:31 2016

@author: lenovo
"""



import urllib2
from bs4 import BeautifulSoup
import re
import MySQLdb
import time
import random
import datetime



def getshopinfo():
    conn = MySQLdb.Connect(host='localhost', user='root', passwd='123456', db='zhubajie',charset='utf8')
    cur=conn.cursor()
    query = 'select * from shopurllist_copy limit 1;'
    cur.execute(query)
    shopinfo = cur.fetchone()
    cur.close()
    conn.close()
    return shopinfo

def getpage(shopinfo):
    my_userAgent=[
                    "Mozilla/5.0 (Windows NT 5.1; rv:37.0) Gecko/20100101 Firefox/37.0",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
                    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
                    "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"]
    user_agent = random.choice(my_userAgent)
    headers={
                    "Referer":str(shopinfo),
                    "User-Agent":user_agent
                    }
        
    url = shopinfo +'/skill.html'
    request = urllib2.Request(url,headers = headers)
    trytimes = 0
    while trytimes <5:
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            soup = BeautifulSoup(content)
            trytimes = 6
        except :
            trytimes = trytimes + 1
            #if hasattr(e,"code"):
             #   print e.code
            #if hasattr(e,"reason"):
               # print e.reason
            time.sleep(5)
            print('连接错误，正在进行第%d次重试'%(trytimes))
    return soup
'''    
def getpage(shopinfo):
    try:
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        url = shopinfo +'/skill.html'
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
    
'''    
    
def getitems(shopinfo,soup):
    items = ['shopid_0',
             'shopname_1',
             'shopurl_2',
             'security money_3',
             'location province_4',
             'location city_5',
             'service type_6',
             'level value_7',
             'threee month money_8',
             'three month deals_9',
             'ongoing money_10',
             'ongoing deals_11',
             'evluation rate_12',
             'evluation score_13',
             'Credibility degree_14',
             'quality score_15',
             'speed score_16',
             'attitude socre_17',
             'total deal number_18',
             'total deal money_19']
    items[0] = shopinfo[0]
    items[1] = shopinfo[1]
    items[2] = shopinfo[2]
    try:
        items[3] = soup.find('p', class_="witkey-security-money-p").contents[1].text    
    except:
        items[3] = '0'
    locationtext = soup.find('p', class_="ads").text.encode('utf-8')
    if '-' in locationtext:
        loction = re.findall('([^\u4e00-\u9fa5]+)-\s([^\u4e00-\u9fa5]+)',locationtext)[0]    
    else:
        loction = [locationtext]
        loction.append('无')
    items[4] = loction[0]
    items[5] = loction[1]
    service = []
    serviceitems = soup.find_all('a',class_='mr5')
    for serviceitem in serviceitems:
        service.append(serviceitem.text.encode('utf-8'))
    items[6] = ','.join(service)
    levelvalue = soup.find('div', class_="ui-user-body").contents[1].text
    if levelvalue == '0':
        for i in range(7,20):
            items[i] = '0'
    else:
        items[7] =levelvalue
        span =soup.find_all('span', class_="orange",style="font-weight:bold;")
        for i in range(7):
            items[i+8] = span[i].text
        score = soup.find_all('span', class_="high")
        for i in range(3):
            items[i+15] = score[i].text
        total_deal_number = 0
        total_deal_money = 0
        deals = soup.find_all('ul', class_="sanc-list")
        for deal in deals:
            total_deal_number = total_deal_number + int(deal.contents[1].contents[1].contents[1].contents[1].text.encode('utf-8'))
            total_deal_money = total_deal_money + float(deal.contents[1].contents[1].contents[1].contents[3].text.encode('utf-8'))
        items[18] = str(total_deal_number)
        items[19] = str(total_deal_money)
    return items

     
def writeSQL(itemsget):
    try:
        items = itemsget
        conn = MySQLdb.Connect(host='localhost', user='root', passwd='123456', db='zhubajie',charset='utf8')
        cur=conn.cursor()
        cur.execute('insert ignore into shopinfo_copy values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',items)
        conn.commit()
        delete = 'delete from shopurllist_copy where shopid = %s'%(itemsget[0])
        cur.execute(delete)
        conn.commit()
        cur.execute('select count(1) from shopurllist_copy;')
        remainning = cur.fetchone()
        print('剩余%d条服务商信息未获取'%(remainning[0]))
        cur.execute('select count(1) from shopinfo_copy;')
        get = cur.fetchone()
        print('已获取%d条服务商信息'%(get[0]))
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
         print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    return

def deleteshop(shopinfo):
    conn = MySQLdb.Connect(host='localhost', user='root', passwd='123456', db='zhubajie',charset='utf8')
    cur=conn.cursor()
    delete = 'delete from shopurllist_copy where shopid = %s'%(shopinfo[0])
    cur.execute(delete)
    conn.commit()
    print('服务商 %s 信息已被删除'%(shopinfo[1].encode('utf-8')))
    cur.close()
    conn.close()
    return    
    
    
def mainloop():
    while True:
        print '-------------------------'
       
        print '正在获取下一条服务商URL'
        
        starttime = datetime.datetime.now()
        shopinfo = getshopinfo()
        
        print ("正在获取 %s 服务商数据"%(shopinfo[1].encode('utf-8')))
        soup = getpage(shopinfo[2])
        alert = soup.find('p', class_="alertcont ")
        if alert == None:
            items = getitems(shopinfo,soup)
            print ("正在写 %s 数据进入数据库"%(shopinfo[1].encode('utf-8')))
            writeSQL(items)
        else:
            print('服务商 %s 已被锁定'%(shopinfo[1].encode('utf-8')))
            deleteshop(shopinfo)
        time.sleep(2)
        endtime = datetime.datetime.now()
        timeoffset = str((endtime-starttime).seconds)+'.'+str((endtime - starttime).microseconds)[0:3]
        print ('此条信息用时%s'%(timeoffset))        
        print '-------------------------'
        

mainloop()

'''
def getpage(shopinfo):
    try:
        my_userAgent=[
                    "Mozilla/5.0 (Windows NT 5.1; rv:37.0) Gecko/20100101 Firefox/37.0",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
                    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
                    "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"]
        user_agent = random.choice(my_userAgent)
        headers={
                    "Referer":str(shopinfo),
                    "User-Agent":user_agent
                    }
        
        url = shopinfo +'/skill.html'
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
'''





