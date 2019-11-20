# -*- coding: utf-8 -*-
import requests
import re
import time
import os
import ctypes
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from lxml import etree
from multiprocessing.dummy import Pool
session = requests.Session()


'''Windows CMD命令行颜色'''

# 句柄号
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# 前景色
FOREGROUND_BLACK = 0x0  # 黑
FOREGROUND_BLUE = 0x01  # 蓝
FOREGROUND_GREEN = 0x02  # 绿
FOREGROUND_RED = 0x04  # 红
FOREGROUND_INTENSITY = 0x08  # 加亮

# 背景色
BACKGROUND_BLUE = 0x10  # 蓝
BACKGROUND_GREEN = 0x20  # 绿
BACKGROUND_RED = 0x40  # 红
BACKGROUND_INTENSITY = 0x80  # 加亮

colors = [FOREGROUND_BLUE,  # 蓝字
          FOREGROUND_GREEN,  # 绿字
          FOREGROUND_RED,  # 红字
          FOREGROUND_BLUE | FOREGROUND_INTENSITY,  # 蓝字(加亮)
          FOREGROUND_GREEN | FOREGROUND_INTENSITY,  # 绿字(加亮)
          FOREGROUND_RED | FOREGROUND_INTENSITY,  # 红字(加亮)
          FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_BLUE | BACKGROUND_INTENSITY]  # 红字蓝底
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_cmd_color(color, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

def reset_color():
    set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

def print_color_text(color, text):
    set_cmd_color(color)
    sys.stdout.write('\n%s\n' % text)  # ==> print(text)
    reset_color()

#转换章节名数字
def huan(i):
    if i < 10:
        i = '00' + str(i)
    elif 10 <= i and i < 100:
        i = '0' + str(i)
    else:
        i = str(i)
    return i

def download(url,i,title,name):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.4; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",

    }
    if i<10:
        i = '00'+str(i)
    elif 10<=i and i<100:
        i ='0'+str(i)
    else:
        i=str(i)
    path= name
    if not os.path.exists(path):
        os.mkdir(path)
    path = name + '/' + title
    if not os.path.exists(path):
        os.mkdir(path)

    r = session.get(url, headers=header)
    if r.status_code != 404:

        with open( '%s/%s/%s.jpg'%(name,title,i), 'wb') as f:
            f.write(r.content)

        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, "下载成功"+ title + ' '+ i)
        return

    return


def imglist(url,title,name):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('log-level=3')
    browser = webdriver.Chrome(options=chrome_options)
    browser.set_page_load_timeout(15)
    xin=0
    abc = 1
    while abc < 100:
        if xin == 1:
            browser.quit()
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            browser = webdriver.Chrome(options=chrome_options)
            browser.set_page_load_timeout(15)
            xin = 0
        try:

            js = " window.open(\'%s\')" % url
            browser.execute_script(js)
            browser.close()
            n = browser.window_handles  # 获取当前页所有窗口句柄

            browser.switch_to.window(n[0])
            source = browser.page_source  # 获取网页源代码

            yeshu = re.findall("<p class=\"img_info\">\(./(.*?)\)</p></div>", source, re.S)[0]
            yeshu = int(yeshu)

            #print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '当前章页数:%d'%yeshu)

            print_color_text(BACKGROUND_GREEN, '开始下载' + title)
            break
        except:
            if abc <= 10:
                print_color_text(FOREGROUND_RED | FOREGROUND_INTENSITY, '抓取当前章页数失败,3秒后自动尝试')
                abc = abc + 1
                time.sleep(10)
                xin=1
                continue
            else:
                print_color_text(FOREGROUND_RED | FOREGROUND_INTENSITY, '抓取当前页数失败,是否重试')
                print_color_text(FOREGROUND_RED | FOREGROUND_INTENSITY, '跳过此章')
                break
    list=[]
    xin = 0
    for i in range(1,yeshu + 1):
        ade=1
        while ade<=20:
            img = url + '?p=%d' % i
            if xin == 1:
                browser.quit()
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('log-level=3')
                browser = webdriver.Chrome(options=chrome_options)
                browser.set_page_load_timeout(15)
            try:
                js = " window.open(\'%s\')" % img
                browser.execute_script(js)
                browser.close()
                n = browser.window_handles  # 获取当前页所有窗口句柄
                browser.switch_to.window(n[0])
                source = browser.page_source  # 获取网页源代码
                # 解析网页，获取下载图片的网址
                # print(source)
                html = etree.HTML(source)
                html_data = html.xpath('/html/body/div[2]/div[4]/div/img/@src')[0]
                # t1 = threading.Thread(target=download(html_data,yeshu,title,name))
                # t1.start()
                #print(html_data)
                list.append(str(html_data))
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, "获取图片链接成功" + title +' '+str(i))
                #print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '获取' + title + '第'+ i  )
                #download(html_data, i, title, name)
                break
            except:
                if ade <= 10:
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '抓取当前章页面失败,3秒后自动尝试')
                    ade = ade + 1
                    time.sleep(10)
                    xin=1
                    continue
                else:
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '抓取当前页面失败,是否重试')
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '跳过此张')
                    break
    pool = Pool(10)
    for imgurl,i in zip(list,range(1,yeshu + 1)):
        pool.apply_async(download, (imgurl, i, title, name,))
    pool.close()
    pool.join()
    print_color_text(FOREGROUND_GREEN | FOREGROUND_INTENSITY, '下载完成第' + title)
    browser.quit()

def list(listurl):

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.4; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",

    }
    mulu=requests.get(listurl,headers=header)
    title = etree.HTML(mulu.text)
    title_url =title.xpath('/html/body/div[3]/div[1]/div[5]/div[3]/ul/li/a/@href')
    title_name = title.xpath('/html/body/div[3]/div[1]/div[5]/div[3]/ul/li/a/@title')
    manhua_name =re.findall("<div class=\"comic_deCon autoHeight\">.*?<h1>(.*?)</h1>", mulu.text, re.S)[0]

    tou='https://www.manhuadui.com'

    p = Pool(3)
    for url,zhang, in zip(title_url,title_name):
        '''
        url:观看链接
        zhang:单章标题
        manhua_name:漫画名
        '''
        #对章节名进行处理

        url= tou+url
        p.apply_async(imglist,(url,zhang,str(manhua_name),))
        #imglist(url,zhang,str(manhua_name))
    p.close()
    p.join()

def dan():
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '输入漫画单话网址:')
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '举个例子:https://www.manhuadui.com/manhua/suishendaizhenvshenhuang/429280.html')
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '输入网址:')
    url=input()
    url = url.replace(' ', '')
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.4; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",

    }
    html=requests.get(url,headers=header)

    title = re.findall("<div class=\"head_title\"><h1><a href=\".*?\">(.*?)</a></h1>-", html.text, re.S)[0]
    zhang=re.findall("<div class=\"head_title\"><h1><a href=\".*?\">.*?</a></h1>-.*?<h2>(.*?)</h2></div>", html.text, re.S)[0]
    #print(title)
    #print(zhang)
    imglist(url,zhang,title)


def quan():
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '输入漫画目录网址:')
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '举个例子:https://www.manhuadui.com/manhua/jinjidejuren/')
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '请输入网址:')
    listurl = input()
    listurl = listurl.replace(' ', '')
    list(listurl)

if __name__ == '__main__':
    a = 1
    while a==1:
        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '输入选项')
        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '1-下载全部章节')
        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '2-下载指定章节')
        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '3-退出程序')
        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '请输入选项')

        while a==1:
            i=input()
            if i=='1':
                quan()
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '全部下载完成')
                break
            if i == '2':
                dan()
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '单章下载完成')
                break
            if i == '3':
                break
            else:
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '请输入正确的选项')
                continue
        if i == '3':
            break
