# BGMの鳴っている部分の音量をゼロにして盛り上がりの検索をしやすいようにするプログラム
import time
import ffmpy
import scipy.io.wavfile
import numpy as np
from numba.decorators import jit
from numpy import sum as npsum
import sys

# mp4ファイルからwavファイルを生成する
def wav_generator(filename):

    ff = ffmpy.FFmpeg(
    inputs = {filename+".mp4" :None},
    outputs = {filename+".wav" :None}
    )

    ff.run()

def threshold_generator(waveform,bins):
    # waveformは x*2のクソなが行列だけどどっちかの列のデータしか多分いらないので[:,0]で一列目のデータだけ扱う
    try:
        new_waveform = np.abs(waveform[:, 0])
    except:
        new_waveform = np.abs(waveform)

    new_waveform_hist, new_waveform_bin = np.histogram(new_waveform, bins=bins)
    s_max = (0, -10)
    len_of_new_waveform_hist = len(new_waveform_hist)
    for th in range(len(new_waveform_hist) + 1):

        n1 = npsum(new_waveform_hist[:th])
        n2 = npsum(new_waveform_hist[th:])

        if n1 == 0:
            mu1 = 0
        else:
            #mu1 = sum([i * new_waveform_hist[i] for i in range(0, th)]) / n1
            mu1 = npsum(np.arange(0, th) * new_waveform_hist[0:th])/ n1
        if n2 == 0:
            mu2 = 0
        else:
            #mu2 = sum([i * new_waveform_hist[i] for i in range(th, len(new_waveform_hist))]) / n2
            mu2 = npsum(np.arange(th, len_of_new_waveform_hist) * new_waveform_hist[th:len_of_new_waveform_hist])/ n2

        s = n1 * n2 * (mu1 - mu2) ** 2
        if s > s_max[1]:
            s_max = (th, s)

    return s_max[0]

# 発話部分を1,それ以外を0とするリストrecording_arrを生成
@jit
def voice_part_converter(last_new_waveform3,len_of_last_new_waveform3,th_min,th_max,range_sums,between_th,zero_rate):

    recording_arr = np.zeros(len_of_last_new_waveform3)
    for th in range(len_of_last_new_waveform3):

        #th_max_value = last_new_waveform3[th_max]
        #th_min_value = last_new_waveform3[th_min]

        if(th_min<0):
            range_sums += last_new_waveform3[th_max]
            if (range_sums/ th_max) * 100 <= zero_rate:
                recording_arr[th] = 1
            print(th)

        if(th_min>=0)and(th_max<len_of_last_new_waveform3):
            range_sums += last_new_waveform3[th_max]
            range_sums -= last_new_waveform3[th_min]
            if (range_sums/between_th)*100 <=zero_rate:
                recording_arr[th] = 1
            print(th)

        if(th_max>=len_of_last_new_waveform3):
            range_sums -= last_new_waveform3[th_min]
            if (range_sums/(len_of_last_new_waveform3-th_min))*100 <=zero_rate:
                recording_arr[th] = 1
            print(th)

        th_min += 1
        th_max += 1

    return recording_arr

def voice_part_converter2(last_new_waveform3,len_of_last_new_waveform3,th_max,zero_rate):
    # 億*億の行列を用意すると死ぬ
    ones_matrix = np.array(np.ones((len_of_last_new_waveform3, len_of_last_new_waveform3)), dtype=np.float32)
    ones_matrix = np.triu(ones_matrix, k=-(th_max - 1))
    ones_matrix = np.triu(ones_matrix.T, k=-(th_max - 1)).T

    ones_sum_arr = np.sum(ones_matrix, axis=0)

    doted_matrix = np.dot(last_new_waveform3, ones_matrix)

    result_arr = (doted_matrix / ones_sum_arr) * 100
    result_arr = np.where((result_arr <= zero_rate), 1, 0)
    print("complete")

    return result_arr
# 発話部分の開始地点と終了地点の集合をリスト化したものを生成　# 1を見つけたらチェックを開始して、0になったらその一個前のインデックスを記録してチェックを外す

@jit
def voice_part_converter3(last_new_waveform3,len_of_last_new_waveform3,th_max,between_th,zero_rate):

    ones_arr = np.ones(between_th,dtype=np.float32)

    # convolveは右側が逆順になるので注意。今回は1だけの配列なのでいいけど
    convolved_arr = np.convolve(last_new_waveform3,ones_arr)
    len_of_convolved_arr = len(convolved_arr)

    if (len_of_convolved_arr% 2 == 0):
        divide_arr = np.concatenate((np.arange(1, int(len_of_convolved_arr / 2)+1,dtype=np.float32) , np.arange(int(len_of_convolved_arr / 2), 0, -1,dtype=np.float32)), axis=0)
    else:
        divide_arr = np.concatenate((np.arange(1, int(len_of_convolved_arr / 2)+1,dtype=np.float32) , np.arange(int(len_of_convolved_arr / 2) +1, 0, -1,dtype=np.float32)), axis=0)

    divide_arr = np.where((divide_arr >= between_th), between_th, divide_arr)
    result_arr = (convolved_arr / divide_arr)*100
    result_arr = np.where((result_arr <= zero_rate), 1, 0)

    recording_arr = result_arr[th_max- 1:-th_max]


    if (len_of_last_new_waveform3 == len(recording_arr)):
        print("OK!")
        return recording_arr
    else:
        print("ERROR!")
        sys.exit()


@jit
def start_end_point_searcher(modified_recording_arr):

    check_start2 = 0
    start_end_pair = ""
    all_start_end_pair_str = ""
    len_of_mra = len(modified_recording_arr)

    for num2,rec2 in enumerate(modified_recording_arr):

        if(num2!= len_of_mra-1):

            if(rec2 ==1) and (check_start2==0):
                start_end_pair = str(num2)+","
                check_start2 =1


            if ((rec2 == 0) and (check_start2 == 1)):
                start_end_pair += str(num2-1)
                start_end_pair +=  "\n\t"
                all_start_end_pair_str += start_end_pair
                start_end_pair = ""
                check_start2 = 0


        if ((num2 == len_of_mra-1)and(check_start2==1)):
            start_end_pair += str(num2-1)
            start_end_pair +=  "\n\t"
            all_start_end_pair_str += start_end_pair
            start_end_pair = ""
            check_start2 = 0

    start_end_pair_list = all_start_end_pair_str.split("\t")

    return start_end_pair_list

# start_end_points.txt を返す. start_end_points.txt は["start,end" , "start,end" …]という形
def start_end_points_generator(input_file_name,bins,filter_range,zero_rate):

    filename = input_file_name.replace(".mp4","")
    wav_generator(filename)

    wav_filename = filename + ".wav"
    sampling_rate, waveform = scipy.io.wavfile.read(wav_filename)
    waveform = np.array(waveform,dtype=np.float32)
    # tは閾値
    t = threshold_generator(waveform,bins=bins)

    # waveform,1次元配列だったり2次元配列だったりするのでそれを考慮する
    try:
        last_new_waveform = waveform[:,0]
    except:
        last_new_waveform = waveform

    #  x<|t|の音をカットする
    last_new_waveform1 = np.where((0<=last_new_waveform)&(last_new_waveform<=t),0,last_new_waveform)
    last_new_waveform2 = np.where((-t<=last_new_waveform1)&(last_new_waveform1<=0),0,last_new_waveform1)

    # 0の部分がtrue(1),それ以外がfalse(0)のnp配列
    last_new_waveform3 = (last_new_waveform2==0)
    last_new_waveform3 = np.array(last_new_waveform3,dtype=np.float32)
    th_min = - int(filter_range*sampling_rate)
    th_max = int(filter_range*sampling_rate)
    between_th = th_max - th_min
    range_sums = np.sum(last_new_waveform3[:th_max-1])
    len_of_last_new_waveform3 = len(last_new_waveform3)

    #recording_arr = voice_part_converter(last_new_waveform3, len_of_last_new_waveform3, th_min, th_max, range_sums, between_th,zero_rate=zero_rate)
    #recording_arr = voice_part_converter2(last_new_waveform3, len_of_last_new_waveform3, th_max, zero_rate)
    recording_arr = voice_part_converter3(last_new_waveform3, len_of_last_new_waveform3, th_max, between_th, zero_rate)

    modified_recording_arr = recording_arr.copy()

    # all_start_end_pair_strは "start_point,end_point\n\t start_point,end_point\n\t…" みたいなデータなので\tでsplitすると良い分割ができる
    start_end_pair_list = start_end_point_searcher(modified_recording_arr)

    with open("start_end_points.txt", mode='w', encoding="utf-8") as f:
        f.writelines(start_end_pair_list)


