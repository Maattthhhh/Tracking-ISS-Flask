from flask import Flask, render_template
import re
import bs4
import requests
import json
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from geopy.geocoders import Nominatim
import urllib.parse
from lxml import etree
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    cleaned_text = ""
    #sends request to get the latitude and longitude of the International Space Station
    req = requests.get('https://api.wheretheiss.at/v1/satellites/25544', timeout=3)
    data = req.json()
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    wikimage_src = "static/globe.gif"

    print("ISS Latitude: ", latitude)
    print("ISS Longitude: ", longitude)

    #uses an API to locate which city, country and/or continent the coordinates point towards
    req = requests.get("https://api.bigdatacloud.net/data/reverse-geocode-client?latitude="+str(latitude)+"&longitude="+str(longitude)+"&localityLanguage=en")
    if req.status_code == 200:
        iss = req.json()

        def get_condition(city):
            url = "http://wttr.in/" + city + "?format=%t"
            page = uReq(url)
            raw = page.read()
            condition = raw.decode("utf-8")
            return condition

        if "GMT" in iss['locality'] or iss['locality'] =='':
            if "GMT" in iss['countryName'] or iss['countryName'] =='':
                if "GMT" in iss['continent'] or iss['continent'] =='':
                    my_url = "https://en.wikipedia.org/wiki/"+iss['localityInfo']['informative'][0]['name']
                    response = requests.get(my_url)
                    if response.status_code == 200:
                        page_soup = soup(response.content, "html.parser")
                        paragraphs = page_soup.findAll('p')
                        filter_phrases = ["was the", "is the", "are the", "was a", "is a", "are a"]
                        wikimages = page_soup.findAll('img', {'src': re.compile('.*\.png$|.*\.jpg$')})
                        if wikimages:
                            if "Page semi-protected" in wikimages[1]['src']:
                                wikimage_src = wikimages[2]['src']
                            else:
                                wikimage_src = wikimages[1]['src']
                        else:
                            wikimage_src = "static/globe.gif"

                        for p in paragraphs:
                            paragraph_text = p.get_text().lower()
                            if any(phrase in paragraph_text for phrase in filter_phrases):
                                text_with_notations = p.get_text()
                                cleaned_text = re.sub(r'\[\d+\]', '', text_with_notations)
                                print()
                                print("The International Space Station is currently near "+iss['localityInfo']['informative'][0]['name']+".")
                                print()
                                print(cleaned_text)
                                break
                    else:
                        print("The International Space Station is currently near "+iss['localityInfo']['informative'][0]['name']+".")
                else:
                    my_url = "https://en.wikipedia.org/wiki/"+iss['continent']
                    response = requests.get(my_url)

                    #uses webscraping to get general info on the current location through Wikipedia
                    if response.status_code == 200:
                        page_soup = soup(response.content, "html.parser")
                        paragraphs = page_soup.findAll('p')
                        filter_phrases = ["was the", "is the", "are the", "was a", "is a", "are a"]
                        wikimages = page_soup.findAll('img', {'src': re.compile('.*\.png$|.*\.jpg$')})
                        if wikimages:
                            if "Page semi-protected" in wikimages[1]['src']:
                                wikimage_src = wikimages[2]['src']
                            else:
                                wikimage_src = wikimages[1]['src']
                        else:
                            wikimage_src = "static/globe.gif"

                        for p in paragraphs:
                            paragraph_text = p.get_text().lower()
                            if any(phrase in paragraph_text for phrase in filter_phrases):
                                text_with_notations = p.get_text()
                                cleaned_text = re.sub(r'\[\d+\]', '', text_with_notations)
                                print()
                                print("The International Space Station is currently near "+iss['continent'])
                                print()
                                print(cleaned_text)
                                break
                    else:
                        cleaned_text = "The International Space Station is currently near "+iss['continent']+"."
            else:
                my_url = "https://en.wikipedia.org/wiki/"+iss['countryName']
                response = requests.get(my_url)

                if response.status_code == 200:
                    page_soup = soup(response.content, "html.parser")
                    paragraphs = page_soup.findAll('p')
                    filter_phrases = ["was the", "is the", "are the", "was a", "is a", "are a"]
                    wikimages = page_soup.findAll('img', {'src': re.compile('.*\.png$|.*\.jpg$')})
                    if wikimages:
                        if "Page semi-protected" or "Translation_to_english_arrow" in wikimages[1]['src']:
                            wikimage_src = wikimages[2]['src']
                        else:
                            wikimage_src = wikimages[1]['src']
                    else:
                        wikimage_src = "static/globe.gif"

                    for p in paragraphs:
                        paragraph_text = p.get_text().lower()
                        if any(phrase in paragraph_text for phrase in filter_phrases):
                            text_with_notations = p.get_text()
                            cleaned_text = re.sub(r'\[\d+\]', '', text_with_notations)
                            print()
                            print("The International Space Station is currently near "+iss['countryName'])
                            print()
                            print(cleaned_text)
                            break
                else:
                    print()
                    cleaned_text = "The International Space Station is currently near "+iss['countryName']
        else:
            my_url = "https://en.wikipedia.org/wiki/"+iss['locality']
            response = requests.get(my_url)

            if response.status_code == 200:
                page_soup = soup(response.content, "html.parser")
                paragraphs = page_soup.findAll('p')
                filter_phrases = ["was the", "is the", "are the", "was a", "is a", "are a"]
                wikimages = page_soup.findAll('img', {'src': re.compile('.*\.png$|.*\.jpg$')})
                if wikimages:
                    if "Page semi-protected" in wikimages[1]['src']:
                        wikimage_src = wikimages[2]['src']
                    else:
                        wikimage_src = wikimages[1]['src']
                else:
                    wikimage_src = "static/globe.gif"

                for p in paragraphs:
                    paragraph_text = p.get_text().lower()
                    if any(phrase in paragraph_text for phrase in filter_phrases):
                        text_with_notations = p.get_text()
                        cleaned_text = re.sub(r'\[\d+\]', '', text_with_notations)
                        print()
                        print("The International Space Station is currently near "+iss['locality']+", "+iss['countryName']+".")
                        print()
                        print(cleaned_text)
                        break
            else:
                print()
                try:
                    city = iss['locality']
                    encoded_city = urllib.parse.quote(city)
                    condition = get_condition(encoded_city)
                    print("The International Space Station is currently near "+iss['locality']+", "+iss['countryName']+".")
                    cleaned_text = "The current weather in " + city + " is " + condition
                except Exception as e:
                    cleaned_text = "The International Space Station is currently near "+iss['locality']+", "+iss['countryName']+"."

    return render_template('index.html', cleaned_text=cleaned_text, wikimage_src=wikimage_src)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)