import requests, time, json
from bs4 import BeautifulSoup as bs

# link = 'http://www.21cineplex.com/'
# data = requests.get(link).text
# soup = bs(data, 'lxml')
# data = soup.find('select', {'id':'mvsearch'})
# fi = {}
# for a in data.find_all('option'):
#     if a['value'] != '':
#         fi[a.text] = a['value']

ses = requests.session()
link = 'http://www.21cineplex.com/page/ajax-movie-list.php'
data = {'cidy':55}
data = ses.post(link, data=data).text
soup = bs(data, 'lxml')
value = []
title = []
for a in soup.find_all('option'):
    if a['value'] != '':
        value.append(a['value'].split(','))
        title.append(a.text.lower().replace(' ', '-'))
link = 'http://21cineplex.com/page/sched_server.php?mod=playnow&ct=%s&mv=%s' % (value[0][1], value[0][0])
soup = bs(ses.get(link).text, 'lxml')
la, sim = [], []
for a in soup.find_all('a'):
	if a.text == '':
		if sim != []:
			la.append(sim)
		sim = []
	else:
		sim.append(a.text)

for a in range(len(la)-1):
	if la[a][0] == la[a+1][0]:
		la[a+1].remove(la[a+1][0])
		la[a].extend(la[a+1])
		print(la[a].sort())