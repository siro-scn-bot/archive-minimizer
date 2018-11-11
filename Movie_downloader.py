from pytube import YouTube
import re

def movie_downloader(youtube_url):
    # ダウンロードしたいページのurlを入れる
    url = youtube_url
    
    yt = YouTube(url)
    resolution = 0
    tag = ""

    # 音声と映像があり解像度が最も高い映像のタグを取得
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
