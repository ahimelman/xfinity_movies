import json
import urllib2
import requests
import sys
from threading import Thread
from Queue import Queue
from bs4 import BeautifulSoup

concurrent = 400

id_list = []
results = []
count = 0

def doWork():
	while True:
		i = q.get()
		try:
			a = json.load(urllib2.urlopen("http://xfinitytv.comcast.net/api/video/summary/Video-" + i + "?type=json"))
		except (UnicodeDecodeError, urllib2.HTTPError) as e:
			q.task_done()
			continue

		try:
			name = a["name"]
			tomato_score = a["latestReviews"][0]["attributes"]["urnrtcriticSummaryScore"]
			year = a["releaseYear"]
			network = a["videoNetworkRealBrand"]
			d = dict(item.split("=") for item in a["latestReviews"][0]["flattenedReviewAttributes"].split(","))
			reviews = d["urn:rt:criticSummaryCount"]

			if tomato_score > 50 and year > 1970 and int(reviews) > 40:
				results.append((name, tomato_score, year, reviews))
				print >> sys.stderr, name, tomato_score, year, reviews, network
		except (IndexError, KeyError) as e:
			q.task_done()
			continue
		q.task_done()

q = Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()

r  = requests.get("http://xfinitytv.comcast.net/movie.widget")
data = r.text
soup = BeautifulSoup(data)
for s in soup.find_all('a'):
	q.put(s['data-v'])

q.join()

results = list(set(results))
sort = sorted(results, key=lambda tup: tup[1], reverse=True)
for s in sort:
	print s[0], s[1], s[2], s[3]
