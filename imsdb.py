import json
import os
import urllib
from bs4 import BeautifulSoup
import urllib.request
import textract as textract
import string
import os
import re
from tqdm import tqdm

"""
This code was lifted from https://github.com/Aveek-Saha/Movie-Script-Database

Couldn't get the full library to work so instead I just took some stuff from it and added others parts it.

@misc{Saha_Movie_Script_Database_2021,
    author = {Saha, Aveek},
    month = {7},
    title = {{Movie Script Database}},
    url = {https://github.com/Aveek-Saha/Movie-Script-Database},
    year = {2021}
}
"""

def get_imsdb():
    ALL_URL = "https://imsdb.com/all-scripts.html"
    BASE_URL = "https://imsdb.com"
    SOURCE = "imsdb"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

    def get_script_from_url(script_url):
        text = ""

        try:

            if script_url.endswith('.pdf'):
                text = get_pdf_text(script_url, os.path.join(SOURCE, file_name))
                return text

            if script_url.endswith('.html'):
                script_soup = get_soup(
                    script_url)
                if script_soup == None:
                    return text
                if len(script_soup.find_all('td', class_="scrtext")) < 1:
                    return ""
                script_text = script_soup.find_all(
                    'td', class_="scrtext")[0].pre

                if script_text:
                    script_text = script_soup.find_all(
                        'td', class_="scrtext")[0].pre.pre
                    if script_text:
                        text = script_text.get_text()

                    else:
                        script_text = script_soup.find_all(
                            'td', class_="scrtext")[0].pre
                        text = script_text.get_text()
        except Exception as err:
            print(script_url)
            print(err)
            text = ""

        return text

    def get_script_url(movie):
        script_page_url = movie.contents[0].get('href')
        name = movie.contents[0].text
        movie_name = script_page_url.split("/")[-1].strip('Script.html')

        script_page_soup = get_soup(
            BASE_URL + urllib.parse.quote(script_page_url))
        if script_page_soup == None:
            return "", name
        paras = script_page_soup.find_all('p', align="center")
        if len(paras) < 1:
            return "", ""
        script_url = paras[0].contents[0].get('href')

        return script_url, name

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]

    metadata = {}
    soup = get_soup(ALL_URL)
    movielist = soup.find_all('p')

    for movie in tqdm(movielist, desc=SOURCE):
        script_url, name = get_script_url(movie)
        if script_url == "":
            continue

        movie_details_url = BASE_URL + '/scripts/' + name.replace(' ', '%20').replace('-', '%20') + '%20Script.html'
        parsed_html = get_soup(movie_details_url)

        movie_release_url = BASE_URL + '/Movie%20Scripts/' + name.replace(' ', '%20').replace('-', '%20') + '%20Script.html'
        parsed_html_meta = get_soup(movie_release_url)
        release_date = ""
        try: 
            script_details = parsed_html_meta.find_all(class_='script-details')
            for line in str(script_details).splitlines():
                if 'Movie Release Date' in line:
                    release_date_string = striphtml(line)
                    release_date = release_date_string[len(release_date_string)-4:]
        except Exception as err:
            # print(err)
            release_date = ""
            
        script_url = BASE_URL + urllib.parse.quote(script_url)
        file_name = format_filename(name)

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url,
            "release_date": release_date
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        text = get_script_from_url(script_url)

        if text == "" or name == "":
            metadata.pop(name, None)
            continue


        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)


def get_soup(url):
    try:
        page = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'})
        result = urllib.request.urlopen(page)
        resulttext = result.read()

        soup = BeautifulSoup(resulttext, 'html.parser')

    except Exception as err:
        print(err)
        soup = None

    return soup


def format_filename(s):
    valid_chars = "-() %s%s%s" % (string.ascii_letters, string.digits, "%")
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace('%20', ' ')
    filename = filename.replace('%27', '')
    filename = filename.replace(' ', '-')
    filename = re.sub(r'-+', '-', filename).strip()

    return filename


def get_pdf_text(url, name):
    doc = os.path.join("scripts", "temp", name + ".pdf")
    result = urllib.request.urlopen(url)
    f = open(doc, 'wb')
    f.write(result.read())
    f.close()
    try:
        text = textract.process(doc, encoding='utf-8').decode('utf-8')
    except Exception as err:
        print(err)
        text = ""

    return text


def create_script_dirs(source):
    DIR = os.path.join("scripts", "unprocessed", source)
    TEMP_DIR = os.path.join("scripts", "temp", source)
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    return DIR, TEMP_DIR, META_DIR


def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)