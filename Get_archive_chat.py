# youtube liveのアーカイブからコメント情報を取得しtxtで保存するプログラム
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import collections as cl

def get_archive_chat(youtube_url):

    target_url = youtube_url
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-desktop-notifications')
    options.add_argument("--disable-extensions")
    options.add_argument('--blink-settings=imagesEnabled=false')
    dict_str = ""
    next_url = ""
    comment_data = []
    session = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    # まず動画ページにrequestsを実行しhtmlソースを手に入れてlive_chat_replayの先頭のurlを入手
    html = requests.get(target_url)
    soup = BeautifulSoup(html.text, "html.parser")

    for iframe in soup.find_all("iframe"):
        if("live_chat_replay" in iframe["src"]):
            next_url= iframe["src"]


    while(1):

        try:
            # chromedriverを開きnext_urlのソースを入手
            driver = webdriver.Chrome(chrome_options=options, executable_path=r"C:\chromedriver_win32\chromedriver.exe")
            driver.get(next_url)
            #html = session.get(next_url, headers=headers).text
            soup = BeautifulSoup(driver.page_source,"lxml")
            # 必ずquitすること。忘れるとgoogle chromeが開かれまくって大変なことになる
            driver.quit()

            # 次に飛ぶurlのデータをfind_allで探してとりあえずsplitで整形
            for scrp in soup.find_all("script"):
                if "window[\"ytInitialData\"]" in scrp.text:
                    dict_str = scrp.text.split(" = ")[1]

            # javascript表記なのでfalseとtrueの表記を直す
            dict_str = dict_str.replace("false","False")
            dict_str = dict_str.replace("true","True")

            # 辞書形式と認識すると簡単にデータを取得できるが、末尾に邪魔なのがあるので消しておく（おそらく共通で「空白2つ + \n + ;」）
            dict_str = dict_str.rstrip("  \n;")
            # 辞書形式に変換
            dics = eval(dict_str)
            # "https://www.youtube.com/live_chat_replay?continuation=" + continue_url が次のlive_chat_replayのurl

            continue_url = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]

            next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url
            # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
            for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
                #print(samp)
                comment_data.append(str(samp)+"\n")
                print(samp)
            print(next_url)
        # next_urlが入手できなくなったら終わり
        except:
            break

    # comment_data.txt にコメントデータを書き込む
    with open("comment_data.txt", mode='w', encoding="utf-8") as f:
        f.writelines(comment_data)

def get_archive_chat2(youtube_url):

    target_url = youtube_url
    dict_str = ""
    next_url = ""
    comment_data = []
    session = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    # まず動画ページにrequestsを実行しhtmlソースを手に入れてlive_chat_replayの先頭のurlを入手
    html = requests.get(target_url)
    soup = BeautifulSoup(html.text, "html.parser")

    for iframe in soup.find_all("iframe"):
        if("live_chat_replay" in iframe["src"]):
            next_url= iframe["src"]

    while(1):

        try:

            html = session.get(next_url, headers=headers)
            soup = BeautifulSoup(html.text,"lxml")

            # 次に飛ぶurlのデータをfind_allで探してとりあえずsplitで整形
            for scrp in soup.find_all("script"):
                if "window[\"ytInitialData\"]" in scrp.text:
                    dict_str = scrp.text.split(" = ")[1]

            # javascript表記なのでfalseとtrueの表記を直す
            dict_str = dict_str.replace("false","False")
            dict_str = dict_str.replace("true","True")

            # 辞書形式と認識すると簡単にデータを取得できるが、末尾に邪魔なのがあるので消しておく（おそらく共通で「空白2つ + \n + ;」）
            dict_str = dict_str.rstrip("  \n;")
            # 辞書形式に変換
            dics = eval(dict_str)
            # "https://www.youtube.com/live_chat_replay?continuation=" + continue_url が次のlive_chat_replayのurl

            continue_url = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]

            next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url
            # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
            for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
                #print(samp)
                comment_data.append(str(samp)+"\n")
                print(samp)
            print(next_url)
        # next_urlが入手できなくなったら終わり
        except:
            break

    # comment_data.txt にコメントデータを書き込む
    with open("comment_data.txt", mode='w', encoding="utf-8") as f:
        f.writelines(comment_data)

