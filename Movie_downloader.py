from pytube import YouTube
import re

def movie_downloader(youtube_url):
    # ダウンロードしたいページのurlを入れる
    url = youtube_url

    # 変数ytに入れる
    yt = YouTube(url)

    resolution = 0
    tag = ""

    # 音声と映像が入っていて解像度が最も大きい映像のタグを取得する
    for lis in yt.streams.all():
        print(lis)
        if "mp4" in str(lis) and "vcodec" in str(lis) and "acodec" in str(lis):
            if resolution < int(re.split(r" res=\"|p\" fps=",str(lis))[1]):
                resolution = int(re.split(r" res=\"|p\" fps=",str(lis))[1])
                tag = re.split(r" itag=\"|\" mime_type", str(lis))[1]

    print(tag)

    # get_by_itagとdownloadでダウンロード
    yt.streams.get_by_itag(tag).download(filename='youtube_video')
    print("download complete!")