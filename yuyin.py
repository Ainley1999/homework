# coding:utf-8 
# 语音识别的测试文件

import pyaudio
import wave
import requests
import json
import base64
import os
import pyttsx3


# 实现录音的函数
def LuYin(time, filename):
	CHUNK = 1024 # wav文件是由若干个CHUNK组成的， CHUNK我们可以理解成数据包或者数据片段
	FORMAT = pyaudio.paInt16 # 这个参数后面写的pyaudio.paInt16表示我们使用量化为数16位来进行录音
	CHANNELS = 1 # 单声道
	RATE = 16000 # 采样率
	RECORD_SECONDS = time #采样时间，单位是秒，上限是60s
	WAVE_OUTPUT_FILENAME = filename # 输出文件名

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		frames_per_buffer=CHUNK)

	print("* 录音开始")

	frames = []

	for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)

	print("* 录音结束")

	stream.stop_stream()
	stream.close()
	p.terminate()


	# 音频流写入文件
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

# 播放音频的函数
def playAudio(filename):
	chunk = 1024

	f = wave.open(filename, 'rb')

	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
		channels=f.getnchannels(),
		rate=f.getframerate(),
		output=True)

	data = f.readframes(chunk)

	# 播放
	print('开始播放')
	while len(data) > 0:
		stream.write(data)
		#print(data)
		data = f.readframes(chunk)

	print('播放结束')

	stream.stop_stream()
	stream.close()

	p.terminate()

# 获取tokent的函数
def Gettokent():
	baidu_server = "https://openapi.baidu.com/oauth/2.0/token?"
	grant_type = "client_credentials"

	client_id = "gmv8IazNOaIZcYKozc50LT8k"

	client_secret = "xYdqHdOMcNhuYdmQLpzkKL9y6zs7DuRD"

	url = baidu_server + 'grant_type=client_credentials&client_id={}&client_secret={}'.format(client_id, client_secret)

	res = requests.post(url)

	token = json.loads(res.text)['access_token']
	
	return token


# 返回识别到的文字的函数
def printText(fileurl):
    try:
        RATE = "16000"                  #采样率16KHz
        FORMAT = "wav"                  #wav格式
        CUID = "wate_play"
        DEV_PID = "1536"                #无标点普通话
        token = Gettokent()

        # 以字节格式读取文件之后进行编码
        with open(fileurl, "rb") as f:
            speech = base64.b64encode(f.read()).decode('utf8')

        size = os.path.getsize(fileurl)
        headers = {'Content-Type': 'application/json'}
        url = "https://vop.baidu.com/server_api"
        data = {
            "format": FORMAT,
            "rate": RATE,
            "dev_pid": DEV_PID,
            "speech": speech,
            "cuid": CUID,
            "len": size,
            "channel": 1,
            "token": token,
        }
        req = requests.post(url, json.dumps(data), headers)
        result = json.loads(req.text)
        return result["result"][0][:-1]
    except:
        return '识别不清'


# 文字转语音的函数
def textToAudio(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def main():
	fileurl = 'E:/a/test.wav'
	LuYin(8,fileurl)
	playAudio(fileurl)
	print(printText(fileurl))
	textToAudio(printText(fileurl))

if __name__ == '__main__':
	main()