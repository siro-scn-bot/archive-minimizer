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
    DEVELOPER_KEY = "your DEVELOPER_KEY"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


    video_url = "https://www.youtube.com/watch?v=" + live_video_id
    video_id = live_video_id
    print(video_id)

    th1 = threading.Thread(target=mov_dl, args=([video_url]))
    th2 = threading.Thread(target=get_arc, args=([video_url]))

    th1.start()
    th2.start()

    th1.join()
    th2.join()

    input_file_name = "youtube_video.mp4"
    Start_end_points_generator.start_end_points_generator(input_file_name,bins=6000,filter_range=0.09,zero_rate=80)

    topic_graph_data_sec = Topic_graph_generator.topic_graph_generator(time_delta_sec=5, rug_sec=9, climax_number=10)
    
    start_timedelta_arr = Start_end_modifier.start_end_modifier(input_file_name, topic_graph_data_sec, lengthen_range=0.5,shorten_range=0.3, margin_range=0.05)
    print(start_timedelta_arr)
    Movie_generator.movie_generator(start_timedelta_arr, input_file_name, output_file_name)
    
