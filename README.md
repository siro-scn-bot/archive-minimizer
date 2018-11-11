# archive-minimizer

## Description
youtubeの生放送のアーカイブからダイジェスト動画を生成するプログラムです。チャットのリプレイが可能なアーカイブのみに対応しています。

アーカイブの動画とチャットをダウンロードし、チャットのタイムスタンプから生放送の盛り上がりを推定。また動画から会話をしているとみられる領域を大まかに推定し、推定された盛り上がりと発話領域から、なるべく会話がぶつ切りにならないように盛り上がっている部分を切り取ったダイジェストを生成します。

処理にかかる時間は動画のダウンロード時間を除くと、1時間のアーカイブに対し4～5分ほどです。

3時間のアーカイブまでは処理できるのを確認していますが、あまり長すぎるとエラーが発生する可能性があります。

実行環境はpython3.6です。
## Requirement
BeautifulSoup

google-api-python-client-py3

pytube

scipy

numpy

ffmpy

numda


上記のpythonモジュールに加えffmpegを利用しているので、ffmpegを使えるようダウンロードしてパスを通しておいてください。
## Usage
「特定のyoutubeチャンネル（複数可）の全てのアーカイブをダイジェスト化する」使い方と「特定のアーカイブのダイジェスト化する」使い方2通りあるので記します。
  
  
  
・「特定のyoutubeチャンネル（複数可）の全てのアーカイブをダイジェスト化する」場合

1.archive-minimizer以下のすべてのファイルを同じフォルダに入れておきます。

2.minimizer_controller.pyのchannelid_dictの内容を「"適当な名前"："アーカイブ化したいyoutubeチャンネルのチャンネルid"」という形式に変更します。現状ではアイドル部全員のチャンネルidが入っています（チャンネルidとは「https://www.youtube.com/channel/????」 という形式のURLの????の部分です）

3.minimizer_controller.pyを実行します。

この場合出力されるダイジェスト動画ファイルは「適当な名前_動画id.mp4」という名前になります。　　


  
・「特定のアーカイブのダイジェスト化する」場合

1.archive-minimizer以下のすべてのファイルを同じフォルダに入れておきます。

2.適当なpythonファイル(test.pyとします)を作り以下のようにコードを書きます。

    #import Live_archive_minimizer
    #Live_archive_minimizer.live_archive_minimizer(live_video_id,output_filename)
    
live_video_idはダイジェストを作りたい動画の動画id、output_filenameは出力される動画ファイルの名前（拡張子不要）を入力します。（動画idとは「https://www.youtube.com/watch?v=????」 という形式のURLの????の部分です）

3.test.pyを実行します。

この場合出力されるダイジェスト動画ファイルは「output_filename.mp4」という名前になります。
　　

  
どちらを使う場合においても、Live_archive_minimizer.pyのパラメーターを変化させることでダイジェスト動画の内容を調整することができます。

それぞれコードを参照しながら説明します。☆が付いているパラメーターは好みで調節したほうが良いですが、それ以外はあまり変更しないほうが良いです。
　　

  
Start_end_points_generator.start_end_points_generator(input_file_name,bins=6000,filter_range=0.09,zero_rate=80)　について

  #binsを増やすと発話領域とそれ以外を分離する閾値が厳密になるが、処理時間が増えます。

  #filter_rangeを増やすと発話部分と認識される部分が増えるが、本来発話部分でない部分をそれと認識する量も増える。0.07～0.11あたりが妥当。

  #zero_rateの範囲は0 < zero_rate < 100。zero_rateを上げると発話部分だと認識される部分が増えるが雑音を除去しにくくなる。zero_rateを上げると雑音を除去しやすくなるが発話部分と認識される部分が減る。70～80あたりが妥当。
　　

  
topic_graph_data_sec = Topic_graph_generator.topic_graph_generator(time_delta_sec=5, rug_sec=9, climax_number=10) について
  #☆ time_delta_secは盛り上がりの間隔を何秒単位で区切るかと、1つのパートの秒数。整数値のみ。5～10秒が妥当。

  #☆ rug_secは発話からコメントがyoutubeに表示されるまでのラグの秒数. 8～10秒が妥当.小数点以下にも対応しているが、最終的に小数点3位までに値が丸め込まれるのでそれ以上記述する意味はない。

  #☆ climax_numberはいくつの盛り上がりを切り取るかの数。整数値のみ。約time_delta_sec*climax_number秒の動画が出力されることになる。
　　

  
start_timedelta_arr = Start_end_modifier.start_end_modifier(input_file_name, topic_graph_data_sec, lengthen_range=0.5,shorten_range=0.3, margin_range=0.05) について
 
  #lengthen_rangeは補正時に動画を前後幅どこまで長くするかの許容値。topic_graph_data_secが5のときlengthen_rangeが0.5だと、1つのパートの長さが5～6(5 + 0.5*2)秒になる。

  #shorten_rangeeは補正時に動画を前後幅どこまで短くするかの許容値。topic_graph_data_secが5のときshorten_rangeが0.3だと、1つのパートの長さが4.4～5(5 - 0.3*2)秒になる。

  #margin_rangeは発話領域とそうでない領域のちょうど境界で動画が切れると違和感が発生する場合があるため、余分に動画を長く・または短くする値。0.05が妥当。
