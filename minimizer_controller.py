from googleapiclient.discovery import build
import Live_archive_minimizer
from bs4 import BeautifulSoup
import requests

channelid_dict ={"dotlive":"UCAZ_LA7f0sjuZ1Ni8L2uITw",
                "mememe":"UCz6Gi81kE6p5cdW1rT0ixqw",
                "chieri":"UCP9ZgeIJ3Ri9En69R0kJc9Q",
                 "tama":"UCOefINa2_BmpuX4BbHjdk9A",
                 "mochi":"UC02LBsjt_Ehe7k0CuiNC6RQ",
                 "suzu":"UCUZ5AlC3rTlM-rA2cj5RP6w",
                 "futaba":"UC5nfcGkOAm3JwfPvJvzplHg",
                 "pino": "UCMzxQ58QL4NNbWghGymtHvw",
                 "iroha": "UCiGcHHHT3kBB1IGOrv7f3qQ",
                 "natori": "UC1519-d1jzGiL1MPTxEdtSA",
                 "azuki": "UCmM5LprTu6-mSlIiRNkiXYg",
                 "iori": "UCyb-cllCkMREr9de-hoiDrg",
                 "ubiba": "UC6TyfKcsrPwBsBnx2QobVLQ",
                 "riko":"UCKUcnaLsG2DeQqza8zRXHiA"}

# 認証に必要なデータ
DEVELOPER_KEY = "your DEVELOPER_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


for vtuber_name, channel_id in channelid_dict.items():

    videos = []
    pageToken_str = ""
    video_ids = []
    live_video_ids = []
    file_data = []
    output_file_names = []

    while (pageToken_str is not None):

        # "channel_id"にあるコンテンツを検索する
        search_response = youtube.search().list(channelId=channel_id, part="id,snippet", maxResults=50, order="date",
                                                pageToken=pageToken_str).execute()

        # 全てのvideのvideo_idを取得
        for result in search_response["items"]:
            try:
                print(result["id"]["videoId"])
                video_ids.append(result["id"]["videoId"])
            except:
                pass

        # nextPageTokenをpageTokenに代入して次のページを読み込む
        pageToken_str = search_response.get("nextPageToken")

    # videoidの中からアーカイブのvideoidだけ抽出する
    for videoid in video_ids:

        next_url = ""
        target_url = "https://www.youtube.com/watch?v=" + videoid
        responses = youtube.videos().list(part="snippet,status,liveStreamingDetails",id=videoid).execute()
        html = requests.get(target_url)
        soup = BeautifulSoup(html.text, "html.parser")

        # 生放送のアーカイブでもチャット欄が存在しない可能性があるので判定
        for iframe in soup.find_all("iframe"):
            if ("live_chat_replay" in iframe["src"]):
                next_url = iframe["src"]

        # 動画が生放送のアーカイブならidを保存
        if responses["items"][0].get("liveStreamingDetails",None) is not None:
            if len(next_url)!=0:
                print(responses["items"][0]["snippet"]["title"])
                print("https://www.youtube.com/watch?v=" + videoid)
                live_video_ids.append(videoid)
                output_file_names.append(vtuber_name + "_" + videoid)
                file_data.append(vtuber_name + "_" + videoid + ".mp4" + "\t" + responses["items"][0]["snippet"]["title"] + "\t" + "https://www.youtube.com/watch?v=" + videoid + "\n")


    # 生放送のvideo_idをtxtに書き出し
    with open("{}_live_videos.txt".format(vtuber_name), mode='w', encoding="utf-8") as f:
        f.writelines(file_data)

    for num,live_video_id in enumerate(live_video_ids):
        Live_archive_minimizer.live_archive_minimizer(live_video_id,output_filename=output_file_names[num])

