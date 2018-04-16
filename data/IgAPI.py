import requests, json
from bs4 import BeautifulSoup

class IgAPI:
	def igpost(self, username):
		links = "https://www.instagram.com/{}/?__a=1".format(username)
		data = requests.get(links).json()
		print json.dumps(data, indent=4)