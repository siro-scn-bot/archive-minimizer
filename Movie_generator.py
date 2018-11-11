import subprocess
import os

def movie_generator(start_timedelta_arr,input_file_name,output_file_name):

    for start_timedelta in start_timedelta_arr:
        cmd = "ffmpeg -ss {} -i {} -t {} part{}.mp4".format(start_timedelta[0], input_file_name, start_timedelta[1], start_timedelta[0])
        subprocess.call(cmd, shell=True)

     # 動画の結合に必要なfile2.txt作成のために"file 各動画の名前.mp4"のリストを作成
    file_names = ["file part{}.mp4".format(start_timedelta[0]) + "\n" for start_timedelta in start_timedelta_arr]

    with open("filenames.txt", "w", encoding="utf-8") as f:
        f.writelines(file_names)

    # files.txtの情報をもとに動画を連結する
    cmd = "ffmpeg -safe 0 -f concat -i filenames.txt -c:v copy -c:a copy -map 0:v -map 0:a {}.mp4".format(output_file_name)
    subprocess.call(cmd, shell=True)

    for start_timedelta in start_timedelta_arr:
        os.remove("part{}.mp4".format(start_timedelta[0]))

    os.remove(input_file_name)
    os.remove(input_file_name.replace(".mp4",".wav"))