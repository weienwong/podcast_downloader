import feedparser
import requests
from lxml import html
import sys

def get_jre_podcast_url():
    feed_url = 'http://podcasts.joerogan.net/feed'
    d = feedparser.parse(feed_url)
    listings = d.entries

    for l in listings:
        title = l['title']
        summary = l['summary_detail']['value']
        episode_number = summary.encode('ascii', 'ignore').split('.')[0]

        filename = "JRE " + episode_number + " - " + title + ".mp3"

        print(filename)

        podcast_url = l['links'][0]['href']
        page = requests.get(podcast_url)
        tree = html.fromstring(page.content)

        path = '/html/body/div[2]/div/div[1]/div[1]/div/div/div[2]/div/ul/li[3]/a/@href'

        podcast_url = tree.xpath(path)[0]
        print(podcast_url)

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


def main():
    get_jre_podcast_url()

if __name__ == "__main__":
    main()