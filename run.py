from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from openai import OpenAI
import time
import os
import pyaudio
import wave

import speech_recognition as sr

def audio_to_text(audio_file):
	recognizer = sr.Recognizer()
	with sr.AudioFile(audio_file) as source:
		audio_data = recognizer.record(source)  

	try:
		text = recognizer.recognize_google(audio_data)
		print("text:", text)
		return text
	except sr.UnknownValueError:
		print("speech recognition sucks")
	except sr.RequestError as e:
		print(f"request error")


def record_audio(filename, duration=5):
	channels = 1
	sample_rate = 16000  
	chunk_size = 1024
	format = pyaudio.paInt16

	p = pyaudio.PyAudio()

	print('recording')
	stream = p.open(format=format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk_size)
	frames = []

	for _ in range(0, int(sample_rate / chunk_size * duration)):
		data = stream.read(chunk_size)
		frames.append(data)

	print('recording stopped')
	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(filename, 'wb')
	wf.setnchannels(channels)
	wf.setsampwidth(p.get_sample_size(format))
	wf.setframerate(sample_rate)
	wf.writeframes(b''.join(frames))
	wf.close()

	return audio_to_text(filename)




client = OpenAI(api_key='') #replace api key

dirname = os.path.dirname(__file__)
chrome_driver_path = os.path.join(dirname, 'chromedriver-mac-x64/chromedriver')
service = Service(executable_path=chrome_driver_path)

driver = webdriver.Chrome(service=service)
driver.get('https://news.ycombinator.com/item?id=40172319')
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40173914');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40167933');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40154053');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40170955');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40170955');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40170373');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40166516');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40172133');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40156890');")
driver.execute_script("window.open('https://news.ycombinator.com/item?id=40166116');")





tab_data = {}
tab_id = 0

for handle in driver.window_handles:
	driver.switch_to.window(handle)
	title = driver.title
	headings = driver.find_elements("xpath", '//h1 | //h2 | //h3 | //h4 | //h5 | //h6')
	paragraphs = driver.find_elements("tag name", 'p')
	tab_data[tab_id] = (title, ' '.join([heading.text for heading in headings]), ' '.join([paragraph.text for paragraph in paragraphs]), handle)
	tab_id += 1
user_audio = record_audio('audio.wav')
prompt = 'I have some browser tabs with text on them. The following text contains a unique identifier for each tab as well as the tab title, headings, and paragraphs:\n\n'
for tab_id in tab_data:
	data = tab_data[tab_id]
	prompt += 'Unique identifier: ' + str(tab_id) + '\n'
	prompt += 'Tab title: ' + data[0] + '\n'
	prompt += 'Tab headings: ' + data[1] + '\n'
	prompt += 'Tab paragraphs: ' + data[2] + '\n'
	prompt += '\n\n'

prompt += 'That is all the tab data. What comes next is a small text description. I want you to choose the tab that best fits the description and output its unique identifier and only its unique identifier.\n\n'
prompt += user_audio
print(prompt)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
    {"role": "system", "content": prompt},
  ]
)

digit_list = [i for i in completion.choices[0].message.content.split() if i.isdigit()]
switchId = int(''.join(digit_list)) 
print('switching to', tab_data[switchId][0])
driver.switch_to.window(tab_data[switchId][3])
time.sleep(10)
driver.quit()
