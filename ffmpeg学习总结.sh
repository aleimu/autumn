# FFmpeg常用命令:
语法：ffmpeg [[options][-i input_file]]… {[options] output_file}…
常用参数说明：
    -i 设定输入流
    -f 设定输出格式
    -ss 开始时间
    视频参数：
    -b 设定视频流量，默认为200Kbit/s
    -r 设定帧速率，默认为25
    -s 设定画面的宽与高
    -aspect 设定画面的比例
    -vn 不处理视频
    -vcodec 设定视频编解码器，未设定时则使用与输入流相同的编解码器
    音频参数：
    -ar 设定采样率
    -ac 设定声音的Channel数
    -acodec 设定声音编解码器，未设定时则使用与输入流相同的编解码器
    -an 不处理音频

1. 视频转换
比如一个avi文件，想转为mp4，或者一个mp4想转为ts。 
ffmpeg -i input.avi output.mp4 
ffmpeg -i input.mp4 output.ts

2. 提取音频
ffmpeg -i test.mp4 -acodec copy -vn output.aac 
上面的命令，默认mp4的audio codec是aac,如果不是，可以都转为最常见的aac。 
ffmpeg -i test.mp4 -acodec aac -vn output.aac

3. 提取视频
ffmpeg -i input.mp4 -vcodec copy -an output.mp4

4. 视频剪切
下面的命令，可以从时间为00:00:15开始，截取5秒钟的视频。 
ffmpeg -ss 00:00:15 -t 00:00:05 -i input.mp4 -vcodec copy -acodec copy output.mp4 
-ss表示开始切割的时间，-t表示要切多少。上面就是从15秒开始，切5秒钟出来。

5. 码率控制
ffmpg控制码率有3种选择，-minrate -b:v -maxrate 
-b:v主要是控制平均码率。 
比如一个视频源的码率太高了，有10Mbps，文件太大，想把文件弄小一点，但是又不破坏分辨率。 
ffmpeg -i input.mp4 -b:v 2000k output.mp4 
上面把码率从原码率转成2Mbps码率，这样其实也间接让文件变小了。目测接近一半。 
不过，ffmpeg官方wiki比较建议，设置b:v时，同时加上 -bufsize 
-bufsize 用于设置码率控制缓冲器的大小，设置的好处是，让整体的码率更趋近于希望的值，减少波动。（简单来说，比如1 2的平均值是1.5， 1.49 1.51 也是1.5, 当然是第二种比较好） 
ffmpeg -i input.mp4 -b:v 2000k -bufsize 2000k output.mp4

-minrate -maxrate就简单了，在线视频有时候，希望码率波动，不要超过一个阈值，可以设置maxrate。 
ffmpeg -i input.mp4 -b:v 2000k -bufsize 2000k -maxrate 2500k output.mp4

6. 视频编码格式转换
比如一个视频的编码是MPEG4，想用H264编码，咋办？ 
ffmpeg -i input.mp4 -vcodec h264 output.mp4 
相反也一样 
ffmpeg -i input.mp4 -vcodec mpeg4 output.mp4

当然了，如果ffmpeg当时编译时，添加了外部的x265或者X264，那也可以用外部的编码器来编码。（不知道什么是X265，可以 Google一下，简单的说，就是她不包含在ffmpeg的源码里，是独立的一个开源代码，用于编码HEVC，ffmpeg编码时可以调用它。当然 了，ffmpeg自己也有编码器） 
ffmpeg -i input.mp4 -c:v libx265 output.mp4 
ffmpeg -i input.mp4 -c:v libx264 output.mp4

7. 只提取视频ES数据
ffmpeg –i input.mp4 –vcodec copy –an –f m4v output.h264

8. 过滤器的使用
    8.1 将输入的1920x1080缩小到960x540输出:
    ffmpeg -i input.mp4 -vf scale=960:540 output.mp4 
    //ps: 如果540不写，写成-1，即scale=960:-1, 那也是可以的，ffmpeg会通知缩放滤镜在输出时保持原始的宽高比。

    8.2 为视频添加logo
    比如，我有这么一个图片 
    iqiyi logo 
    想要贴到一个视频上，那可以用如下命令： 
    ./ffmpeg -i input.mp4 -i iQIYI_logo.png -filter_complex overlay output.mp4 
    结果如下所示： 
    add logo left 
    要贴到其他地方？看下面： 
    右上角： 
    ./ffmpeg -i input.mp4 -i logo.png -filter_complex overlay=W-w output.mp4 
    左下角： 
    ./ffmpeg -i input.mp4 -i logo.png -filter_complex overlay=0:H-h output.mp4 
    右下角： 
    ./ffmpeg -i input.mp4 -i logo.png -filter_complex overlay=W-w:H-h output.mp4

    8.3 去掉视频的logo
    语法：-vf delogo=x:y:w:h[:t[:show]] 
    x:y 离左上角的坐标 
    w:h logo的宽和高 
    t: 矩形边缘的厚度默认值4 
    show：若设置为1有一个绿色的矩形，默认值0。

    ffmpeg -i input.mp4 -vf delogo=0:0:220:90:100:1 output.mp4 
    结果如下所示： 
    de logo

9. 截取视频图像
ffmpeg -i input.mp4 -r 1 -q:v 2 -f image2 pic-%03d.jpeg 
-r 表示每一秒几帧 
-q:v表示存储jpeg的图像质量，一般2是高质量。 
如此，ffmpeg会把input.mp4，每隔一秒，存一张图片下来。假设有60s，那会有60张。


可以设置开始的时间，和你想要截取的时间。 
ffmpeg -i input.mp4 -ss 00:00:20 -t 10 -r 1 -q:v 2 -f image2 pic-%03d.jpeg 
-ss 表示开始时间 
-t 表示共要多少时间。 
如此，ffmpeg会从input.mp4的第20s时间开始，往下10s，即20~30s这10秒钟之间，每隔1s就抓一帧，总共会抓10帧。

 
10. 序列帧与视频的相互转换
把darkdoor.[001-100].jpg序列帧和001.mp3音频文件利用mpeg4编码方式合成视频文件darkdoor.avi：
$ ffmpeg -i 001.mp3 -i darkdoor.%3d.jpg -s 1024x768 -author fy -vcodec mpeg4 darkdoor.avi

还可以把视频文件导出成jpg序列帧：
$ ffmpeg -i bc-cinematic-en.avi example.%d.jpg






# 参考链接
http://www.ffmpeg.org/
http://www.cnblogs.com/hongyanee/p/3310087.html
https://www.cnblogs.com/jiangzhaowei/p/8270782.html
https://blog.csdn.net/u012868357/article/details/80240639
http://www.ffmpeg.org/sample.html
https://blog.csdn.net/cug_heshun2013/article/details/79518632


# FFserver服务器实现WebM格式视频直播

#1.配置服务器端口
Port 8090
BindAddress 0.0.0.0
MaxHTTPConnections 2000
MaxClients 1000
MaxBandwidth 30000
CustomLog -
NoDaemon
#NoDefaults

#2.配置ffm文件
<Feed feed1.ffm>
File ./feed1.ffm
FileMaxSize 100M
</Feed>

#3.配置流
<Stream test1.flv>
Feed feed1.ffm
Format flv
VideoFrameRate 24
VideoBitRate 1280
VideoSize 1280x720
NoAudio
</Stream>

<Stream test.webm>              # Output stream URL definition
   Feed feed1.ffm              # Feed from which to receive video
   Format webm

   # Audio settings
   AudioCodec vorbis
   AudioBitRate 64             # Audio bitrate

   # Video settings
   VideoCodec libvpx
   VideoSize 720x576           # Video resolution
   VideoFrameRate 25           # Video FPS
   AVOptionVideo flags +global_header  # Parameters passed to encoder
                                       # (same as ffmpeg command-line parameters)
   AVOptionVideo cpu-used 0
   AVOptionVideo qmin 10
   AVOptionVideo qmax 42
   AVOptionVideo quality good
   AVOptionAudio flags +global_header
   PreRoll 15
   StartSendOnKey
   VideoBitRate 400            # Video bitrate
</Stream>

#4.status.html
<Stream status.html>
Format status
# ACL allow localhost
# ACL allow 172.16.2.195
</Stream>


# 启动服务
ffserver -f ffserver.conf

# 装填视频源
ffmpeg -i example.flv http://localhost:8090/feed1.ffm
ffmpeg -i example.mp4 http://172.16.4.120:8090/feed1.ffm

# 输出的视频地址为
http://172.16.4.120:8090/test1.flv

# 访问流
ffplay http://localhost:8090/test1.flv
ffplay http://172.16.4.120:8090/test1.flv




