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
from colorama import Fore

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=chrome_options)

browser.set_page_load_timeout(15)
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



# See "http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp" for information on Windows APIs.

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

#传入图片链接，图片第几张，漫画第几话,漫画名
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

# 抓取页面中的图片链接
def imgurl(url,yeshu,title,name):
 # 最大待时间为30s

    # 当加载时间超过30秒后，自动停止加载该页面
    try:
        js = " window.open(\'%s\')" % url
        browser.execute_script(js)
        browser.close()
        n = browser.window_handles  # 获取当前页所有窗口句柄

        browser.switch_to.window(n[0])


        source = browser.page_source  # 获取网页源代码


    except TimeoutException:
        browser.execute_script('window.stop()')
    # 解析网页，获取下载图片的网址
    #print(source)
    html = etree.HTML(source)
    html_data = html.xpath('/html/body/div[2]/div[4]/div/img/@src')[0]
    #t1 = threading.Thread(target=download(html_data,yeshu,title,name))
    #t1.start()
    download(html_data,yeshu,title,name)




    #download(str(html_data))

#抓取页面所有张数链接
def imglist(url,title,name):
    for abd in range(100):
        for cde in range(100):
            try:
                js = " window.open(\'%s\')" %url
                browser.execute_script(js)
                browser.close()
                n = browser.window_handles  # 获取当前页所有窗口句柄

                browser.switch_to.window(n[0])
                source = browser.page_source  # 获取网页源代码


            except TimeoutException:
                browser.execute_script('window.stop()')

            try:
                yeshu=re.findall("<p class=\"img_info\">\(./(.*?)\)</p></div>", source, re.S)[0]
                yeshu=int(yeshu)
                break

            except:
                if cde <=3:
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '抓取页数失败,3秒后自动尝试')
                    time.sleep(3)
                if cde >3:
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '抓取页数失败,是否重试')
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '1-重试')
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '2-跳过')
                    num=input()
                    num=int(num)
                    if num == 1:
                        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '正在重试')
                    if num == 2:
                        print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '跳过此章')
                        break
        try:
            print(yeshu)
            print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, yeshu)
            print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY,'开始下载'+title)

            for i in range(1, yeshu + 1):
                    img = url + '?p=%d' % i
                    #p.apply_async(imgurl(str(img), i, title, name))

                    imgurl(str(img),i,title,name)

                    # print(imgurl)

            print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '下载完成'+title)
            break
        except:
            print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '下载失败' + title)
            if abd <= 3:
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '抓取页数失败,3秒后自动尝试')
                time.sleep(3)
            if abd > 3:
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '抓取页数失败,是否重试')
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '1-重试')
                print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '2-跳过')
                num = input()
                num = int(num)
                if num == 1:
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '正在重试')
                if num == 2:
                    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '跳过此章')
                    break








def list(listurl):
    global chrome_options
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.4; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",

    }
    mulu=requests.get(listurl,headers=header)
    title = etree.HTML(mulu.text)
    title_url =title.xpath('/html/body/div[3]/div[1]/div[5]/div[3]/ul/li/a/@href')
    title_name = title.xpath('/html/body/div[3]/div[1]/div[5]/div[3]/ul/li/a/@title')
    manhua_name =re.findall("<div class=\"comic_deCon autoHeight\">.*?<h1>(.*?)</h1>", mulu.text, re.S)[0]

    tou='https://www.manhuadui.com'
    for url,zhang in zip(title_url,title_name):


        url= tou+url
        #print(url,zhang,str(manhua_name))
        imglist(url,zhang,str(manhua_name))





if __name__ == '__main__':

    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, '输入漫画目录网址:')
    listurl=input()
    listurl=listurl.replace(' ','')
    #listurl=os.sys.argv[1]
    list(listurl)
    browser.quit()
    print_color_text(FOREGROUND_BLUE | FOREGROUND_INTENSITY, "全部下载完成")

