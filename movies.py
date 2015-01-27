import json
import urllib2
import requests
import sys
from bs4 import BeautifulSoup

r  = requests.get("http://xfinitytv.comcast.net/movie.widget")
data = r.text
soup = BeautifulSoup(data)

id_list = []
results = []
count = 0

for s in soup.find_all('a'):
	id_list.append(s['data-v'])

for i in id_list:
	try:
		a = json.load(urllib2.urlopen("http://xfinitytv.comcast.net/api/video/summary/Video-" + i + "?type=json"))
	except (UnicodeDecodeError, urllib2.HTTPError) as e:
		pass

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
		pass

results = list(set(results))
sort = sorted(results, key=lambda tup: tup[1], reverse=True)
for s in sort:
	print s[0], s[1], s[2], s[3]
