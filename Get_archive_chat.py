from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import collections as cl

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

            for scrp in soup.find_all("script"):
                if "window[\"ytInitialData\"]" in scrp.text:
                    dict_str = scrp.text.split(" = ")[1]

            dict_str = dict_str.replace("false","False")
            dict_str = dict_str.replace("true","True")

            dict_str = dict_str.rstrip("  \n;")
            # 辞書形式に変換
            dics = eval(dict_str)
            # "https://www.youtube.com/live_chat_replay?continuation=" + continue_url が次のlive_chat_replayのurl

            continue_url = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]

            next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url
            # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
            for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
                comment_data.append(str(samp)+"\n")
                print(samp)
            print(next_url)
        # next_urlが入手できなくなったら終わり
        except:
            break

    # comment_data.txt にコメントデータを書き込む
    with open("comment_data.txt", mode='w', encoding="utf-8") as f:
        f.writelines(comment_data)

