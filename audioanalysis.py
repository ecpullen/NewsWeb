from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import urllib
import urllib2
from bs4 import BeautifulSoup
import os
from pytube import YouTube


def search(search_string):
	links = []
	textToSearch = search_string
	query = urllib.quote(textToSearch)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, "html5lib")
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'})[:5]:
		print(vid['href'])
		links.append('https://www.youtube.com' + vid['href'])
	return links

def dl_audio(vid_link, i):
	try:
		print(vid_link)
		yt = YouTube(vid_link)
		print("pre-filter")
		title = "vid_" + str(i)
		yt.streams.filter().all()
		print("pre_stream")
		stream = yt.streams.first()
		print(stream.download(filename = title))
		return title+".mp4"
	except:
		pass

def download_vids(links):
	return_string_list = []
	for i in range(len(links)):
		return_string_list.append(dl_audio(links[i], i))
	return return_string_list

def transcribe_model_selection(speech_file, model, language):
	try:
		client = speech.SpeechClient()
		print("speech_file")
		print(speech_file)
		with open(speech_file, 'rb') as audio_file:
   			content = audio_file.read()
			audio = types.RecognitionAudio(content=content)
		print("pre-config")
		config = speech.types.RecognitionConfig(
        		encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        		sample_rate_hertz=16000,
        		language_code=language)
		print("pre-response")
		response = client.recognize(config, audio)
		print("response")
		print(response)
		for result in response.results:
			print('Transcript: {}'.format(result.alternatives[0].transcript))
	except:
		print("error")
	response = client.recognize(config, audio)
urls = download_vids(search("abcnews"))
print(urls)
for path in urls:
	print(path)
	if(path):
		transcribe_model_selection(path, "video", "en-US")
	else:
		print("No Path")
