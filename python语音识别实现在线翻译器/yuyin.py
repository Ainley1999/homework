# coding:utf-8 
# 语音识别的py文件

import pyaudio # 进行录音的第三方库
import wave # 将录音流转成wav文件的第三库
import requests # 请求在线翻译的第三方库
import pyttsx3 # 将返回的文字转为语音的第三方库
from aip import AipSpeech # 调用百度语音识别的第三方库
import tkinter # 绘图的第三方库
import tkinter.messagebox # gui的对话框信息
from PIL import ImageTk, Image # 对于对话框中的背景图片用到的库
import os # 最后将生成的录音wav文件删除用到了这个库


# 使用baidu_aip要用到的变量
APP_ID = '17607474'
API_KEY = 'gmv8IazNOaIZcYKozc50LT8k'
SECRET_KEY = 'xYdqHdOMcNhuYdmQLpzkKL9y6zs7DuRD'
client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)



# 实现录音的函数
def LuYin(Time, filename, label):
	CHUNK = 1024 # wav文件是由若干个CHUNK组成的， CHUNK我们可以理解成数据包或者数据片段
	FORMAT = pyaudio.paInt16 # 这个参数后面写的pyaudio.paInt16表示我们使用量化为数16位来进行录音
	CHANNELS = 1 # 单声道
	RATE = 16000 # 采样率
	RECORD_SECONDS = Time #采样时间，单位是秒，上限是60s
	WAVE_OUTPUT_FILENAME = filename # 输出文件名

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		frames_per_buffer=CHUNK)

	print("* 录音开始") # 在控制台显示

	frames = []

	for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)

	print("* 录音结束") # 在控制台显示

	stream.stop_stream()
	stream.close() # 流已关闭
	p.terminate()

	# 音频流写入文件
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close() # 文件已关闭

# 调用baidu_aip包将语音转文字,不需要联网，直接调用接口
def baidu_aip(fileurl):
	# 读取录音文件
	with open(fileurl,'rb') as fp:
		voices = fp.read()
	try:
		# 参数dev_pid：1536普通话(支持简单的英文识别)、1537普通话(纯中文识别)、1737英语、1637粤语、1837四川话、1936普通话远场
		result = client.asr(voices, 'wav', 16000, {'dev_pid':1536,})
		result_text = result["result"][0]
		print('you said:'+result_text) # 在控制台显示
		return result_text
	except KeyError:
		print('KeyError')

# 文字转语音的函数
def textToAudio(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def youdao(content):
   	# 模拟发送请求
    url="http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
    # 请求头
    header={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    data={}
    data['i']=content
    data['from']='AUTO'
    data['to'] = 'AUTO'
    data['smartresult'] = 'dict'
    data['client'] = 'fanyideskweb'
    data['doctype'] = 'json'
    data['version'] = '2.1'
    data['keyfrom'] = 'fanyi.web'
    data['action'] = 'FY_BY_CLICKBUTTION'
    data['typoResult'] = 'false'
    # 发送post请求 并用result接收返回数据
    result=requests.post(url,data=data,headers=header)
    transl=result.json() # 解析
    translation=transl['translateResult'][0][0]['tgt']

    print("you said :" + translation) # 在控制台显示翻译结果
    return translation

def main():
	fileurl = 'test.wav' # 录音文件会保存在py文件同一路径下

	# 界面的初始化
	root = tkinter.Tk()
	root.title("语音识别——在线翻译")
	root.geometry("300x300")
	root.attributes('-alpha',1)
	textToAudio("主人，语音翻译为您服务，即将打开服务窗口")
	# 设置图片背景
	canvas = tkinter.Canvas(root, width=600, height=400,bd=0,highlightthickness=0)
	imgpath = 'Ainley.png' # 保证图片和该py文件在同一路径下
	img = Image.open(imgpath)
	photo = ImageTk.PhotoImage(img)
	
	canvas.create_image(150,150,image=photo) # 设置x/y偏移量
	canvas.pack()

	label = tkinter.Label(root) # 设置提示标签
	label.pack()
	label.config(text='准备录音')
	def _start():
		label.config(text="录音开始")
		root.update()
		LuYin(3,fileurl,label) # 开始录音并保存文件
		myWord = baidu_aip(fileurl) # 将录音转成文字返回
		label.config(text="录音结束")
		yesOrno = tkinter.messagebox.askyesno('识别正确吗？', myWord) # 返回true or false
		if(yesOrno):
			textToAudio(myWord) # 把我说的话读出来
			if(myWord):
				result = youdao(myWord) # 进入在线翻译（有道）去翻译
				tkinter.messagebox.showinfo('翻译结果正确吗？', result) # 对话框显示翻译结果
				textToAudio(result)
			else:
				tkinter.messagebox.showerror('错误','主人，您的选择有问题！') # 这里是防止点错了
		else:
			tkinter.messagebox.showwarning('警告', '识别错误，您要再说一遍啦！')
		label.config(text='准备录音')
		root.update() # 初始化标签

	button = tkinter.Button(root, text = "语音翻译", command=_start)
	button.pack() # 添加一个按钮

	canvas.create_window(150,150,width=70,height=30,window=button) # 将按钮和标签防止在画布上的指定位置
	canvas.create_window(150,20,width=70,height=30,window=label) 

	root.mainloop() # 进入循环
	textToAudio("翻译任务结束，感谢您的使用")
	os.remove(fileurl)

if __name__ == '__main__':
	main()

# 百度云平台账户ID：bd1b48576d674a5e8dc4ac71f5d6db50
# AppID:17607474
# API Key：gmv8IazNOaIZcYKozc50LT8k
# Secret Key：xYdqHdOMcNhuYdmQLpzkKL9y6zs7DuRD