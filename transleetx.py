from google.cloud import translate
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from bs4 import BeautifulSoup
import requests
import time
from random import randint
import csv

links = {"Australia":"https://news.google.com/news/headlines/section/topic/WORLD?ned=au&hl=en-AU&gl=AU", 
"Brazil":"https://news.google.com/news/headlines/section/topic/WORLD?ned=pt-BR_br&hl=pt-BR&gl=BR", 
"China":"https://news.google.com/news/headlines/section/topic/WORLD?ned=cn&hl=zh-CN&gl=CN", 
"Cuba":"https://news.google.com/news/headlines/section/topic/WORLD?ned=es_cu&hl=es-419&gl=CU", 
"Egypt":"https://news.google.com/news/headlines/section/topic/WORLD?ned=ar_eg&hl=ar-EG&gl=EG", 
"Germany":"https://news.google.com/news/headlines/section/topic/WORLD?ned=de&hl=de&gl=DE", 
"India":"https://news.google.com/news/headlines/section/topic/WORLD?ned=in&hl=en-IN&gl=IN", 
"Japan":"https://news.google.com/news/headlines/section/topic/WORLD?ned=jp&hl=ja&gl=JP", 
"SA":"https://news.google.com/news/headlines/section/topic/WORLD?ned=en_za&hl=en&gl=ZA", 
"UK":"https://news.google.com/news/headlines/section/topic/WORLD?ned=uk&hl=en-GB&gl=GB",
"US":"https://news.google.com/news/headlines/section/topic/WORLD?ned=us&hl=en&gl=US"}

def create_list_of_countries():
	filename = "countries.tsv"
	f = open(filename, 'r')
	countries = {}
	while True:
		new_line = f.readline().lower().strip()
		if new_line == "":
			break
		countries[new_line] = []
	f.close()
	return countries

def scrape_headers(link):
	time.sleep(randint(0, 1))
	r = requests.get(link)
	content = r.text
	headings = []
	soup = BeautifulSoup(content, "html.parser")
	st_divs = soup.findAll("a", {"role": "heading"})
	for st_div in st_divs:
		headings.append(translate_text(st_div.text.lower()))
	return headings

def attribute_country(headings, countries):
	for header in headings:
		# for country in countries.keys():
		for country_name in countries.keys():
			if country_name in header:
				countries.get(country_name).append(header)
	return countries

def attribute_sentiment(countries_dictionary):
	country_scores = {}
	for country in countries_dictionary.keys():
		if len(countries_dictionary.get(country)) != 0:
			country_scores[country] = sentiment_analysis(countries_dictionary.get(country))

	return country_scores

def save_to_tsv(dict, filename = 'test'):
	f = open(filename+'.tsv', 'w')
	for key in dict.keys():
		f.write(key+'\t'+ str(dict.get(key)) +'\n')
	f.close()


def get_sentiment_of_all_countries(link,filename = "test"):
	countries_dict = create_list_of_countries()
	headers_list = scrape_headers(link)
	countries_dict = attribute_country(headers_list, countries_dict)
	data = attribute_sentiment(countries_dict)
	save_to_tsv(data, "australia")
	return data


def translate_text(text, target='en'):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language = target)
    #print("Text: ", result['input'])
    #print("Translation: ", result["translatedText"])
    return result["translatedText"]

def determine_sentiment(s):
    client = language.LanguageServiceClient()
    document = types.Document(
                content=s,
                type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score

def sentiment_analysis(strs):
    return sum([determine_sentiment(s) for s in strs])/len(strs)

def read_web(code):
	return get_sentiment_of_all_countries(links[code],code)

for key in links.keys():
	print(key)
	print(read_web(key))
