import pdfcrowd, os, string
from imgurpython import ImgurClient
from random import *

class ScreenshotWeb():
    def __init__(self, pdfcrowdData, imgurData):
        self.API = pdfcrowd.HtmlToImageClient(pdfcrowdData[0], pdfcrowdData[1])
        self.API.setOutputFormat('png')
        self.API.setScreenshotWidth(1366)
        self.imgur = ImgurClient(imgurData[0], imgurData[1], imgurData[2], imgurData[3])
        self.workdir = os.getcwd()

    def uploader(self, path):
        try:
            data = self.imgur.upload_from_path(path, config=None, anon=False)
            os.remove(path)
            return data['link']
        except Exception as e:
            raise e

    def screenshotWeb(self, query):
        try:
            path = "".join(choice(string.ascii_letters + string.digits) for x in range(10)) + '.jpg'
            if 'http://' not in query and 'https://' not in query:
                query = 'http://' + query
            self.API.convertUrlToFile(query, path)
            return self.uploader(path)
        except Exception as e:
            raise e