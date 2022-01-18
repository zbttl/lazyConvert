import os
from pymediainfo import MediaInfo

filetuple = os.walk(r'./')

#走显存编码,可选qsv/cuda/nvenc/amf,使用qsv时需保证没有独立显卡（特别是N卡），否则会报错，是bug，来自[#6996（尝试在 Windows 10 上使用 NVidia 主 GPU 支持的 Intel 系统上使用 QSV 会导致崩溃）– FFmpeg](https://trac.ffmpeg.org/ticket/6996)，不用可置空。
hwaccel=''
#hwaccel=r' -hwaccel qsv '
#解码方法，可用h264_cuvid/h264_amf/h264_qsv/libx264，不用可置空。
#self_decodec=''
self_decodec=r' -c:v h264_qsv '
#解码方法，可用h264_nvenc/h264_amf/h264_qsv/libx264
#self_encodec=''
self_encodec=r' -c:v h264_qsv '

#码率（单位kbps）
destiny_bitrate=4000
#目标大小(MB)
destiny_space=200
#目标帧数
fps=r'23'
#目标格式
format=r'.mp4'

#转换命令
def change_bat(file_name,extension,bit_rate,height):
    command=r'ffmpeg'+hwaccel+self_decodec+r'-i "'+file_name+extension+r'"'+self_encodec+r' -b:v '+str(bit_rate)+r' -vf scale=-1:'+str(height)+r' -r '+fps+r' -y "'+file_name+r'_convert'+format+r'"'
    os.system(command)

#获取码率
def detect_bit_rate(file_name):
    command=r'ffprobe -i "'+file_name+r'" -show_entries format=bit_rate -v quiet -of csv="p=0"'
    bit_rate=os.popen(command).read().split()[0]
    return bit_rate

#获取视频高度
def detect_height(file_name):
    command=r'ffprobe -i "'+file_name+r'" -show_entries stream=height -v quiet -of csv="p=0"'
    height=os.popen(command).read().split()[0]
    return height


for path,dir_list,files in filetuple:
    for file in files:
        try:
            path=path.strip('./')
            if(path!=''): 
                file=os.path.join(path,file)
            fullfilename=file
            #排除非视频文件
            fileInfo = MediaInfo.parse(file)
            for track in fileInfo.tracks:
                if track.track_type == 'Video':
                    #获取拓展名
                    (file, extension) = os.path.splitext(file)
                    #已转换/直接更名的视频直接跳过
                    if(not fullfilename.endswith(r'convert'+format) and not os.path.exists(file+r'_convert'+format) and not fullfilename.endswith(r'convert'+extension) and not os.path.exists(file+r'_noconvert'+extension)):
                        if(os.path.getsize(file+extension)>destiny_space*1024*1024):
                            #第一次转换，大于目标大小的，码率缩到目标码率，高度缩到1080，若码率和高度均一低于目标码率，则取源文件码率/高度，然后缩减帧率，转换
                            bit_rate= int(detect_bit_rate(file+extension))
                            height=detect_height(file+extension)
                            if(bit_rate>destiny_bitrate*1000):
                                bit_rate=destiny_bitrate*1000
                            if(int(height)>1080):
                                height='1080'
                            print("初次转换视频码率为："+str(bit_rate/1000)+"kbps")
                            change_bat(file,extension,bit_rate,height)
                            #第一次转换后文件仍大于目标大小的，则进入循环转换流程，每次转换码率和高度会同时缩减到上次转换的80%，直到大小低于目标大小为止
                            while(os.path.getsize(file+r'_convert'+format)>destiny_space*1024*1024):
                                bit_rate=int(bit_rate)*4/5;
                                height=int(height)*4/5;
                                print("本次转换视频码率为："+str(int(bit_rate/1000))+"kbps，视频宽度为："+str(height)+"px")
                                change_bat(file,extension,bit_rate,height)
                        else:
                            #未转换，直接复制更名，便于后续筛选
                            all_path=r'copy /y "'+file+extension+r'" "' +file+r'_noconvert'+extension+r'"'
                            os.system(all_path)
        except:
             continue
