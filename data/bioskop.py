import requests
from bs4 import BeautifulSoup as bs

class Bioskop():
    def getAllBioskop(self):
        namabioskop = []
        linkbisokop = []
        for a in range(1, 23):
            link = 'https://jadwalnonton.com/bioskop/?page=' + str(a)
            data = requests.get(link).text
            soup = bs(data, 'lxml')
            for b in soup.find_all('div', {'class':'bg relative'}):
                data = b.find('a', {'href':True})
                namabioskop.append(data.text.replace('\n', ''))
                linkbisokop.append(data['href'])
        return namabioskop, linkbisokop

    def getBioskopKota(self, kota):
        linklist = self.getLinkPage(kota)
        namabioskop = []
        linkbisokop = []
        for link in linklist:
            data = requests.get(link).text
            soup = bs(data, 'lxml')
            for a in soup.find_all('div', {'class':'bg relative'}):
                data = a.find('a', {'href':True})
                namabioskop.append(data.text.replace('\n', ''))
                linkbisokop.append(data['href'])
        return namabioskop, linkbisokop

    def getLinkPage(self, kota):
        link = 'https://jadwalnonton.com/bioskop/di-' + kota
        data = requests.get(link).text
        soup = bs(data, 'lxml')
        halaman = soup.find('div', {'class':'paggingcont'})
        linklist = []
        end = None
        for a in halaman.find_all('a', {'title':True}):
            if 'Halaman' in a['title']:
                end = int(a.text)
        if end != None:
            for a in range(1, end+1):
                linklist.append('https://jadwalnonton.com/bioskop/di-%s/?page=%s' % (kota, str(a)))
        else:
            linklist.append(link)
        return linklist