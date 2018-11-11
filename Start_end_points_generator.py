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
            mu1 = npsum(np.arange(0, th) * new_waveform_hist[0:th])/ n1
        if n2 == 0:
            mu2 = 0
        else:
            mu2 = npsum(np.arange(th, len_of_new_waveform_hist) * new_waveform_hist[th:len_of_new_waveform_hist])/ n2

        s = n1 * n2 * (mu1 - mu2) ** 2
        if s > s_max[1]:
            s_max = (th, s)

    return s_max[0]


@jit
def voice_part_converter3(last_new_waveform3,len_of_last_new_waveform3,th_max,between_th,zero_rate):

    ones_arr = np.ones(between_th,dtype=np.float32)

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

    recording_arr = voice_part_converter3(last_new_waveform3, len_of_last_new_waveform3, th_max, between_th, zero_rate)

    modified_recording_arr = recording_arr.copy()

    start_end_pair_list = start_end_point_searcher(modified_recording_arr)

    with open("start_end_points.txt", mode='w', encoding="utf-8") as f:
        f.writelines(start_end_pair_list)


