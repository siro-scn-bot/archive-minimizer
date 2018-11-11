import Get_archive_chat
import Topic_graph_generator
import subprocess
import threading
import Movie_downloader
from googleapiclient.discovery import build
import Start_end_points_generator
import Start_end_modifier
import Movie_generator
import os


def mov_dl(video_url):
    Movie_downloader.movie_downloader(video_url)
# video_urlの動画のチャット欄のコメント情報を取得し,comment_data.txtに保存する
def get_arc(video_url):
    Get_archive_chat.get_archive_chat2(video_url)

def live_archive_minimizer(live_video_id,output_filename):
    # 認証に必要なデータ
    DEVELOPER_KEY = "AIzaSyCVgpmZ7NlORA4xB8jlo4WIoWxyqiHK1eU"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


    video_url = "https://www.youtube.com/watch?v=" + live_video_id
    video_id = live_video_id
    print(video_id)
    #video_data = youtube.videos().list(id =video_id, part="snippet").execute()
    #input_file_name = video_data["items"][0]["snippet"]["title"] + ".mp4"

    # 最後に出力される動画の名前. 拡張子はナシ
    output_file_name = output_filename #←youtubeのidにする


    th1 = threading.Thread(target=mov_dl, args=([video_url]))
    th2 = threading.Thread(target=get_arc, args=([video_url]))

    th1.start()
    th2.start()

    th1.join()
    th2.join()
    # 動画の音声をもとに発話部分のstart_pointとend_pointの組合せのリストをstart_end_points.txtに保存する
    # binsを増やすと雑音カットの閾値が厳密になるが計算量が上がる.
    # filter_rangeを増やすと発話部分だと認識される部分が増えるが本来発話部分でない部分をそれと認識する量も増えるので0.07～0.11あたりが妥当.
    # zero_rateの範囲は0 < zero_rate < 100. zero_rateを上げると発話部分だと認識される部分が増えるが雑音を除去しにくくなる
    # zero_rateを上げると雑音を除去しやすくなるが発話部分だと認識される部分が減る. 70～80あたりが妥当
    #os.rename(input_file_name,"youtube_video.mp4")
    input_file_name = "youtube_video.mp4"
    Start_end_points_generator.start_end_points_generator(input_file_name,bins=6000,filter_range=0.09,zero_rate=80)
    # youtube liveのコメント情報から盛り上がりの開始時刻のリストを返す
    # time_delta_secは盛り上がりの間隔を何秒単位で区切るかと、1つのパートの秒数. 整数値でないとダメ. 5秒が妥当
    # rug_secは発話からコメントがyoutubeに表示されるまでのラグの秒数. 8～10秒が妥当.小数点以下にも対応しているが、最終的に小数点3位までに値が丸め込まれるのでそれ以上記述する意味はあまりない
    # climax_numberはいくつの盛り上がりを切り取るかの数. 整数値のみ. 12だとだいたい12*5=60秒の動画が生成される
    topic_graph_data_sec = Topic_graph_generator.topic_graph_generator(time_delta_sec=5, rug_sec=9, climax_number=10)
    # lengthen_rangeは補正時に動画を前後幅どこまで長くするかの許容値. lengthen_rangeが0.5だと1つのパートの長さが5～6(5 + 0.5*2)秒になる
    # shorten_rangeeは補正時に動画を前後幅どこまで短くするかの許容値. shorten_rangeが0.3だと1つのパートの長さが4.4～5(5 - 0.3*2)秒になる
    # margin_rangeは発話領域とそうでない領域のちょうど境界で動画が切れると違和感が発生する場合があるため、余分に動画を長く・または短くする値
    # 最終的に3つの補正値を考慮すると4.3～6.1秒が1つのパートの長さになりうる
    start_timedelta_arr = Start_end_modifier.start_end_modifier(input_file_name, topic_graph_data_sec, lengthen_range=0.5,shorten_range=0.3, margin_range=0.05)
    print(start_timedelta_arr)
    Movie_generator.movie_generator(start_timedelta_arr, input_file_name, output_file_name)
    """
    """
    #wavファイルをいつ処理するか 並行処理を行うなら全てを並行処理にしないといけない