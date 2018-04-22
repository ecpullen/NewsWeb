from google.cloud import translate
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from bs4 import BeautifulSoup
import requests
import time
from random import randint
import csv

links = {"AUS":"https://news.google.com/news/headlines/section/topic/WORLD?ned=au&hl=en-AU&gl=AU", 
"BRA":"https://news.google.com/news/headlines/section/topic/WORLD?ned=pt-BR_br&hl=pt-BR&gl=BR", 
"CHN":"https://news.google.com/news/headlines/section/topic/WORLD?ned=cn&hl=zh-CN&gl=CN", 
"CUB":"https://news.google.com/news/headlines/section/topic/WORLD?ned=es_cu&hl=es-419&gl=CU", 
"EGY":"https://news.google.com/news/headlines/section/topic/WORLD?ned=ar_eg&hl=ar-EG&gl=EG", 
"DEU":"https://news.google.com/news/headlines/section/topic/WORLD?ned=de&hl=de&gl=DE", 
"IND":"https://news.google.com/news/headlines/section/topic/WORLD?ned=in&hl=en-IN&gl=IN", 
"JPN":"https://news.google.com/news/headlines/section/topic/WORLD?ned=jp&hl=ja&gl=JP", 
"ZAF":"https://news.google.com/news/headlines/section/topic/WORLD?ned=en_za&hl=en&gl=ZA", 
"GBR":"https://news.google.com/news/headlines/section/topic/WORLD?ned=uk&hl=en-GB&gl=GB",
"USA":"https://news.google.com/news/headlines/section/topic/WORLD?ned=us&hl=en&gl=US",
"RUS":"https://news.google.com/news/headlines?ned=ru_ru&hl=ru&gl=RU" ,
"MEX":"https://news.google.com/news/headlines?ned=es_mx&hl=es-419&gl=MX",
"SWE":"https://news.google.com/news/headlines?ned=sv_se&hl=sv&gl=SE",
"CAN":"https://news.google.com/news/headlines?ned=ca&hl=en-CA&gl=CA",
"FRA":"https://news.google.com/news/headlines?ned=fr&hl=fr&gl=FR"}


# Create primary country list

def create_list_of_countries():
	'''
	This method opens the list of countries from the countries.tsv and returns it as a dictionary in the form:
	[List of names] : [List of headlines (null)]
	'''
	filename = "country_list.csv"
	f = open(filename, 'r')
	countries = {}
	for i in range(191):
		new_line = f.readline().lower().strip().split(',')
		print(new_line)
		countries[new_line[0]] = [new_line[1:],[]]
	f.close()
	return countries

# Scrape

def translate_text(text, target='en'):
	translate_client = translate.Client()
	result = translate_client.translate(text, target_language = target)
	#print("Text: ", result['input'])
	#print("Translation: ", result["translatedText"])
	return result["translatedText"]

def scrape_headers(link):
	'''
	Returns list of translated headings from given link
	'''
	time.sleep(0.2)
	r = requests.get(link)
	content = r.text
	headings = []
	soup = BeautifulSoup(content, "html.parser")
	st_divs = soup.findAll("a", {"role": "heading"})
	for st_div in st_divs:
		headings.append(translate_text(st_div.text).lower())
	return headings

# Sentiment analysis

def attribute_country(headings_list, countries_dict):
	'''
	takes list of general headlines and dictionary of countries and will then 
	attribute the headline to the countries that appear in it
	'''
	for header in headings_list:

		for country_iso in countries_dict.keys():
			for country_name in countries_dict.get(country_iso)[0]:
				try:
					if country_name in header:
						countries_dict.get(country_iso)[1].append(header)
				except:
					print("skipped header")
	return countries_dict

def determine_sentiment(s):
	'''
	returns the sentiment score of the given string s
	'''
	client = language.LanguageServiceClient()
	document = types.Document(
			content=s,
			type=enums.Document.Type.PLAIN_TEXT)
	sentiment = client.analyze_sentiment(document=document).document_sentiment
	return sentiment.score

def sentiment_analysis(strs):
	'''
	returns the mean sentiment for the given list of strings
	'''
	try:
		return sum([determine_sentiment(s) for s in strs[1]])/len(strs[1])
	except:
		print(strs)

def attribute_sentiment(countries_dictionary):
	'''
	This function makes and returns a dictionary containing the countries with their 
	corresponding sentiment scores, leaving None for countries with no data points
	'''
	country_scores = {}
	for country in countries_dictionary.keys():
		try:
			country_scores[country] = sentiment_analysis(countries_dictionary.get(country))+1
		except:
			country_scores[country] = None # possible error

	return country_scores

def save_to_csv(dict, filename):
	'''
	saves the dictionary as a csv file
	'''
	f = open('sentiment.'+filename.lower()+'.csv', 'w')
	f.write("iso3, SENTIMENT\n")
	for key in dict.keys():
		f.write(key.upper()+', '+ str(dict.get(key)) +'\n')
	f.close()

def get_sentiment_of_all_countries(link, countries_dict,  filename = "test"):
	'''
	returns the sentiments for the list of countries
	'''
	#countries_dict = create_list_of_countries() #list of countries
	headers_list = scrape_headers(link) #list of headers
	countries_dict = attribute_country(headers_list, countries_dict) #dictionary with headers and countries
	save_to_csv(countries_dict, filename) #saves the country dictionary to filename, a csv
	data = attribute_sentiment(countries_dict) #data is the sentiment of the list of countries
	save_to_csv(data, filename) #saves data, the sentiment of the list of countries, to filename, a csv
	return data

def read_web(code, dict):	
	return get_sentiment_of_all_countries(links[code], dict, code)

def main():
	keys = links.keys()
	dict = create_list_of_countries()
	for country_iso_code in keys:
		print(read_web(country_iso_code, dict))

# Top level code

if __name__ == "__main__":
	main()



