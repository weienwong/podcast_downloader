import feedparser
import requests
from lxml import html
import sys
import os
from dotenv import load_dotenv

load_dotenv()

API_URL=os.getenv("API_URL") 
DOMAIN=os.getenv("DOMAIN")
API_KEY=os.getenv("API_KEY")

def get_jre_podcast_url():
        feed_url = 'http://podcasts.joerogan.net/feed'
        d = feedparser.parse(feed_url)
        listings = d.entries
        podcast_list_text = ""

        for l in listings:
                title = l['title']
                podcast_url = l['links'][0]['href']
                page = requests.get(podcast_url)
                tree = html.fromstring(page.content)
                path = '/html/body/div[2]/div/div[1]/div[1]/div/div/div[2]/div/ul/li[3]/a/@href'
                podcast_url = tree.xpath(path)[0]
                podcast_list_text += title + " " + podcast_url + "\n"
        
        return podcast_list_text

def download_podcast(url, filename):
        with open(filename, 'wb') as fd:
                r = requests.get(url, stream=True)
                total_length = int(r.headers.get('content-length'))
                dl = 0
                for chunk in r.iter_content(chunk_size=4096):
                        dl += len(chunk)
                        fd.write(chunk)
                        done = int(50 * dl / total_length)
                        percentage_done = int(100 * dl / total_length)
                        sys.stdout.write("\r[{}{}] {}%".format('=' * done, ' ' * (50-done), percentage_done))
                        sys.stdout.flush()
                        sys.stdout.write("\nDownload complete\n")

def send_simple_message(to, subject, text):
        return requests.post(
		"https://api.mailgun.net/v3/" + DOMAIN +"/messages",
		auth=("api", API_KEY),
		data={"from": " <pi@" + DOMAIN +">",
			"to": to,
			"subject": subject,
			"text": text})

def main():
    message = get_jre_podcast_url()
    send_simple_message(["weienwong.93@gmail.com"], "This week's Joe Rogan Experience", message)

if __name__ == "__main__":
    main()