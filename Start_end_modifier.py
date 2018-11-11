import numpy as np
import scipy.io.wavfile
import Start_end_points_generator
import Topic_graph_generator
import subprocess

def start_end_modifier(input_file_name,topic_graph_data_sec,lengthen_range,shorten_range,margin_range):

    start_points = []
    end_points = []

    wav_filename = input_file_name.replace(".mp4",".wav")
    sampling_rate, waveform = scipy.io.wavfile.read(wav_filename)

    with open("start_end_points.txt", mode='r', encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line_list = line.rstrip('\r\n')
            state_list = line_list.split(",")
            start_points.append(state_list[0])
            end_points.append(state_list[1])

    start_points_np = np.array(start_points)
    start_points_np = start_points_np.astype(np.float64)  # float型にしておかないと次の計算でバグる
    start_points_np = start_points_np / sampling_rate
    start_points_np_sec = np.round(start_points_np, 3)

    end_points_np = np.array(end_points)
    end_points_np = end_points_np.astype(np.float64)
    end_points_np = end_points_np / sampling_rate
    end_points_np_sec = np.round(end_points_np, 3)


    # アバウトな盛り上がりのデータを小数点3位までのfloat型に変更
    topic_graph_data_sec = topic_graph_data_sec.astype(np.float64)
    topic_graph_data_sec = np.round(topic_graph_data_sec, 3)

    start_list = []
    end_list = []
    for topic_sec in topic_graph_data_sec:

        for i in range(len(start_points_np_sec)):

            # 動画の切り取り開始時刻 topic_sec が発話部分なら

            if (start_points_np_sec[i] <= topic_sec)and(topic_sec <= end_points_np_sec[i]):
                if (topic_sec -lengthen_range <= start_points_np_sec[i]  and end_points_np_sec[i - 1]  <=topic_sec):
                # もし猶予0.05を取ると別の発話部分を取り込んでしまうなら取り込まないように
                    if (start_points_np_sec[i] - margin_range <=end_points_np_sec[i-1]):
                        start_list.append(end_points_np_sec[i-1] - (start_points_np_sec[i] - end_points_np_sec[i-1])/2)
                        break
                    # そうでないなら start_points_np_sec -0.05を開始地点にする
                    else:
                        start_list.append(start_points_np_sec[i] - margin_range)
                        break

                # 前の方に猶予は取っていいけど後ろの方の猶予はもっとタイトにしないアカンくないか
                if (topic_sec <= start_points_np_sec[i] and end_points_np_sec[i + 1] <= topic_sec + shorten_range):
                    if (start_points_np_sec[i + 1] <= end_points_np_sec[i] + margin_range ):
                        start_list.append(end_points_np_sec[i] + (start_points_np_sec[i+1] - end_points_np_sec[i])/2)
                        break
                    else:
                        start_list.append(end_points_np_sec[i] + margin_range)
                        break

            elif(i==len(start_points_np_sec)-1):
                start_list.append(topic_sec)



        for j in range(len(start_points_np_sec)):
            topic_end_sec = topic_sec + 5

            if (start_points_np_sec[j] <= topic_end_sec)and(topic_end_sec <= end_points_np_sec[j]):
                if (topic_end_sec - shorten_range <= start_points_np_sec[j] and end_points_np_sec[j - 1] <= topic_end_sec):
                    if (start_points_np_sec[j] - margin_range <= end_points_np_sec[j - 1]):
                        end_list.append(end_points_np_sec[j - 1] - (start_points_np_sec[j] - end_points_np_sec[j - 1]) / 2)
                        break

                    else:
                        end_list.append(start_points_np_sec[j] - margin_range)
                        break

                if (topic_end_sec <= start_points_np_sec[j] and end_points_np_sec[j + 1] <= topic_end_sec + lengthen_range):
                    if (start_points_np_sec[j + 1] <= end_points_np_sec[j] + 0.05):
                        end_list.append(end_points_np_sec[j] + (start_points_np_sec[j + 1] - end_points_np_sec[j]) / 2)
                        break
                    else:
                        end_list.append(end_points_np_sec[j] + margin_range)
                        break

            elif(j==len(start_points_np_sec)-1):
                end_list.append(topic_end_sec)


    start_nparr = np.round(start_list, 3)
    end_nparr = np.round(end_list, 3)
    timedelta_nparr = end_nparr - start_nparr
    start_timedelta_arr =  np.c_[start_nparr,timedelta_nparr]


    return start_timedelta_arr