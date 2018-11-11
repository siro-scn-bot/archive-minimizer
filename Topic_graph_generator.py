# コメントとタイムスタンプ. one_cm_dataはcomment_data.txtの一行分のデータ
# print(one_cm_data["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["message"]["simpleText"])
# print(one_cm_data["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"])

# youtube liveのコメント情報から分割された動画を生成するプログラム
import datetime
import numpy as np
import matplotlib.pyplot as plt

# comment_data.txtから読み込んだデータをもとにdatetime型のタイムスタンプのリストを返す
def comment_data_to_timestamp_list(comment_data_file_name):

    comment_data = []
    comment_dateTimestamp_list = []

    with open(comment_data_file_name, "r", encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line_list = line.rstrip('\r\n')
            comment_data.append(line_list)

    # comment_data.txt中のコメントデータからtimestampを抜き出しリスト化する.ノイズを考慮してtryを使う
    # ノイズじゃなくてスパチャのデータとかそんなやつっぽい
    for comment_datum in comment_data:

        try:
            comment_datum_dic = eval(comment_datum)
            # コメントのタイムスタンプをstr型で取得
            comment_timestampText = comment_datum_dic["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"]

            # "12:33"みたいなのをdatetime型に合わせるための変形
            if (len(comment_timestampText.split(":")) == 2):
                comment_timestampText = "0:" + comment_timestampText

            # コメントのタイムスタンプをdatetime型に変形
            comment_dateTimestamp = datetime.datetime.strptime(comment_timestampText, '%H:%M:%S')
            comment_dateTimestamp_list.append(comment_dateTimestamp)

        except:
            pass

    # comment_dateTimestamp_listは時間順にソートされてないことがあるのでソートする
    comment_dateTimestamp_list = sorted(comment_dateTimestamp_list)

    return comment_dateTimestamp_list

# datetime型のタイムスタンプのリストをもとに一定区間ごとの勢いを数値化した値を保持するリストを作る
def timestamp_list_to_climax_list(time_delta_sec):

    # time_delta_sec秒区間ごとの勢いを記録するリスト. index*time_delta_sec + time_delta_sec
    climax_list = [0]

    comment_dateTimestamp_list = comment_data_to_timestamp_list("comment_data.txt")

    # n秒区画ごとの勢いを記録するための準備
    comment_datetime_min = comment_dateTimestamp_list[0]
    comment_datetime_max = comment_datetime_min + datetime.timedelta(seconds=time_delta_sec)

    # n秒区間ごとの勢いを記録するリストを作る
    for comment_datetime_data in comment_dateTimestamp_list:
        # 次のコメントがめっちゃ遠い時comment_datetime_dataがminとmaxの間に入るまでwhileしないといけない
        while(1):
            if comment_datetime_min <= comment_datetime_data < comment_datetime_max:
                climax_list[-1] += 1
                break
            else:
                comment_datetime_min += datetime.timedelta(seconds=time_delta_sec)
                comment_datetime_max += datetime.timedelta(seconds=time_delta_sec)
                # 次のコメントが5秒以上離れていることを考慮する
                if comment_datetime_min <= comment_datetime_data < comment_datetime_max:
                    climax_list.append(1)
                    break
                else:
                    climax_list.append(0)

    return climax_list

def topic_graph_generator(time_delta_sec,rug_sec,climax_number):

    climax_list = timestamp_list_to_climax_list(time_delta_sec)
    print(climax_list)
    # 盛り上がった順(昇順)のインデックスを返す
    graph_data_index = (np.array(climax_list)).argsort()
    # 盛り上がりの箇所をm個取得
    topic_graph_data_index = graph_data_index[-climax_number:]

    # インデックス0を取得してしまったときは排除する(うまく処理できないので)
    if 0 in topic_graph_data_index:
        topic_graph_data_index = graph_data_index[-(climax_number+1):]
        topic_graph_data_index = topic_graph_data_index[~(topic_graph_data_index==0)]

    #topic_graph_data_indexが「盛り上がった順」になっているので、時系列順にするためにsortedを使う
    topic_graph_data_index = np.array(sorted(topic_graph_data_index))
    topic_graph_data_index = topic_graph_data_index.astype(np.float64)
    print(topic_graph_data_index)

    # コメント取得範囲とラグを考慮して「盛り上がりの開始時間のリスト」をtopic_graph_data_secに代入     # 盛り上がりの開始(？)秒数が入っている
    topic_graph_data_sec = topic_graph_data_index*float(time_delta_sec) -float(rug_sec)
    print(topic_graph_data_sec)

    return topic_graph_data_sec
