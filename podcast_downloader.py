import feedparser
import requests
from lxml import html
from dotenv import load_dotenv

from datetime import datetime 
import sys
import os

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
                link =l['link']
                podcast_url = l['links'][0]['href']
                page = requests.get(podcast_url)
                tree = html.fromstring(page.content)
                path = '/html/body/div[2]/div/div[1]/div[1]/div/div/div[2]/div/ul/li[3]/a/@href'
                podcast_url = tree.xpath(path)[0]
                podcast_list_text += title + " " + link + "\nDownload link: " + podcast_url + "\n\n"
        
        return podcast_list_text

def get_sam_harris_making_sense_podcast():
        rss_url = 'http://wakingup.libsyn.com/rss'
        d = feedparser.parse(rss_url)
        listings = d.entries
        podcast_list = ''

        for l in listings:
                title = l['title']
                podcast_url = l.enclosures[0]['href']
                pub_date = l.published

                # ex. Wed, 03 Jul 2019 15:43:59 +0000
                pub_datetime = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S +0000")
                timedelta = datetime.now() - pub_datetime

                if timedelta.days <= 30:
                        listing = title + "\n" + podcast_url + "\n\n"
                        podcast_list += listing       
        return podcast_list

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
        message = ''
        message += "Sam Harris Making Sense Podcast\n"
        message += get_sam_harris_making_sense_podcast()
        message += "\n"
        message += "\n"
        message += "Joe Rogan Experience\n"
        message += get_jre_podcast_url()
        message += "\n"
        message += "\n"
        send_simple_message(["weienwong.93@gmail.com"], "Podcasts", message)


if __name__ == "__main__":
    main()
