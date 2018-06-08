#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import os
import requests                 #简单易用的库
import urllib.parse
import threading  # 多线程

# 设置最大线程锁（可以上10把锁）
thread_lock = threading.BoundedSemaphore(value=10)


# 通过url获取页面的数据（utf-8格式）
def get_page(url):
    '''返回页面的html'''
    # requests自带json.loads(字符串-》字典)
    return requests.get(url).content.decode('utf-8')


def findall_in_page(page, startpart, endpart): 
    '''返回目标信息的list
    page：页面html信息
    startpart：目标信息的前面部分
    endpart：目标信息的后面部分
    '''
    all_strings = []
    end = 0
    while page.find(startpart, end) != (-1):
        start = page.find(startpart, end) + len(startpart)
        end = page.find(endpart, start)
        string = page[start:end]
        all_strings.append(string)
    return all_strings


def pages_from_duitang(label):
    '''label: 搜索的关键词
       返回所有页面的html
    '''
    pages = []          #全部页面的html
    #在network中的xhr里面找到的规律。kw：关键字，start：从第x条信息开始，虽然设置limit为1000,但是该网站动态加载数据，每次只能读100（大概），所以下面range中设置100
    url = 'https://www.duitang.com/napi/blog/list/by_search/?kw={}&start={}&limit=1000'     
    label = urllib.parse.quote(label)               # 将中文转成ascii码
    #for index in range(0, 3600, 100):  #0-3600之间，每次加100
    print(label)
    for index in range(0, 100, 100):
        u = url.format(label, index)
        page = get_page(u)  
        pages.append(page)
    return pages


def pic_urls_from_pages(pages):
    '''返回所有页面的目标字符串的list
    pages：所有页面的html
    '''
    pic_urls = []
    for page in pages:
        urls = findall_in_page(page, '"path":"', '"')  # 注意：冒号后面没有空格
        pic_urls.extend(urls)
    return pic_urls


def download_pics(urls, n):
    r = requests.get(urls)
    path = 'pics\\'+str(n) + '.jpg'
    with open(path, 'wb') as f:
        f.write(r.content)
    thread_lock.release()  # 解锁


def main(label):        # label:搜索的关键字
    pages = pages_from_duitang(label)
    pic_urls = pic_urls_from_pages(pages)
    n = 0
    for url in pic_urls:
        n += 1
        print('正在下载第{}张图片'.format(n))
        thread_lock.acquire()  # 上锁
        t = threading.Thread(target=download_pics, args=(url, n))
        t.start()

main('人')

#游标位置获取信息的方式
#多线程，上锁解锁