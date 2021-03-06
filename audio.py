from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import urllib
import urllib2
from bs4 import BeautifulSoup
import os
import pafy
from google.cloud import storage


def search(search_string):
	links = []
	textToSearch = search_string
	query = urllib.quote(textToSearch)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html,"html.parser")
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'})[:5]:
		print(vid['href'])
		links.append('https://www.youtube.com' + vid['href'])
	return links

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

def dl_audio(vid_link, i):
#	try:
	if vid_link:
		print(vid_link)
		video = pafy.new(vid_link)
		bestaudio = video.getbestaudio()
		print("pre-download")
		bestaudio.download(filepath = "aud_" + str(i) + ".ogg")
		upload_blob('world_news_download_text/', "aud_" + str(i) + ".ogg","aud_" + str(i) + ".ogg")
		print("post-download")
		return "aud_" + str(i) + ".ogg"
#	except:
#		print("failed")
#		pass

def download_vids(links):
	return_string_list = []
	for i in range(len(links)):
		return_string_list.append(dl_audio(links[i], i))
	return return_string_list

def transcribe_model_selection(speech_file, model, language):
#	try:
	if True:
		client = speech.SpeechClient()
		print("speech_file")
		print(speech_file)
		audio =  types.RecognitionAudio(uri = 'gs://world_news_download_test/'+speech_file)
		print("pre-config")
		config = types.RecognitionConfig(encoding = speech.enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        		sample_rate_hertz = 16000,
        		language_code = "en_US")
		print("pre-response")
#	except:
#		pass
	if True:
		operation = client.long_running_recognize(config, audio)
		response = operation.result(timeout = 90)
		print("response")
		print(response)
		for result in response.results:
			print('Transcript: {}'.format(result.alternatives[0].transcript))
		response = client.recognize(config, audio)


print(download_vids(search("abcnews")[1:2]))

