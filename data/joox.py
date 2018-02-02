from bs4 import BeautifulSoup
import requests, json, sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class jooxAPI():
    def render(self, source_url):
        class Render(QWebEngineView):
            def __init__(self, url):
                self.html = None
                self.app = QApplication(sys.argv)
                QWebEngineView.__init__(self)
                self.loadFinished.connect(self._loadFinished)
                #self.setHtml(html)
                self.load(QUrl(url))
                self.app.exec_()

            def _loadFinished(self, result):
                # This is an async call, you need to wait for this
                # to be called before closing the app
                self.page().toHtml(self._callable)

            def _callable(self, data):
                self.html = data
                # Data has been stored, it's safe to quit the app
                self.app.quit()

        return Render(source_url).html

    def durat(self, detik):
        try:
            m, s = divmod(detik, 60)
            if detik >= 3600:
                h, m = divmod(m, 60)
                return str("%d:%02d:%02d" % (h, m, s))
            else:
                return str("%02d:%02d" % (m, s))
        except Exception as e:
            raise e

    def search(self, query):
        link = 'http://www.joox.com/searchResult?q=' + requote_uri(query)
        soup = BeautifulSoup(render(url), 'lxml')
        songid = []
        for a in soup.find_all('a', {'class':'name', 'href':True}):
            if 'single?id' in a['href']:
                songid.append(a['href'][len('#/single?id='):])
        return songid

    def get_data(self, songid):
        link = 'http://api.joox.com/web-fcgi-bin/web_get_songinfo?songid=' + songid
        data = json.loads(requests.get(baseurl).text[len('MusicInfoCallback('):-1])
        result = {
            'image': data['imgSrc'],
            'judul': data['msong'],
            'penyanyi': data['msinger'],
            'album': data['malbum'],
            'durasi': durat(int(data['minterval'])),
            'm4a': data['m4aUrl'],
            'mp3': data['mp3Url'],
            '192bit': data['r192Url'],
            '320bit': data['r320Url']
        }
        return result